import argparse
import datetime
import json
import os
import sys
from dataclasses import dataclass

import pandas as pd

CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))
BACKEND_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from models import db, Dish, DishPrediction, DailyMenu, Window, SystemConfig

try:
    from xgboost import XGBRegressor
except ImportError as e:
    raise ImportError(
        "未安装 xgboost，请先执行: pip install xgboost pandas"
    ) from e


FEATURE_COLUMNS = [
    "dish_id",
    "feature_day_of_week",
    "feature_is_weekend",
    "feature_is_holiday",
    "feature_weather_code",
    "feature_avg_temperature",
    "feature_window_1_online",
    "feature_window_2_online",
    "feature_window_3_online",
    "feature_special_event_code",
]

LABEL_COLUMN = "label_quantity"


@dataclass
class ModelConfig:
    n_estimators: int = 300
    learning_rate: float = 0.05
    max_depth: int = 4
    min_child_weight: int = 1
    subsample: float = 0.9
    colsample_bytree: float = 0.9
    reg_alpha: float = 0.0
    reg_lambda: float = 1.0
    random_state: int = 42
    objective: str = "reg:squarederror"
    eval_metric: str = "mae"


def _to_int_bool(value):
    return 1 if int(value) else 0


def _ensure_parent_dir(path):
    parent = os.path.dirname(path)
    if parent and not os.path.exists(parent):
        os.makedirs(parent, exist_ok=True)


def _validate_training_df(df):
    missing = [c for c in FEATURE_COLUMNS + [LABEL_COLUMN] if c not in df.columns]
    if missing:
        raise ValueError(f"训练数据缺少字段: {missing}")

    for c in FEATURE_COLUMNS + [LABEL_COLUMN]:
        if df[c].isna().any():
            raise ValueError(f"训练数据字段存在空值: {c}")


def load_training_dataframe(csv_path):
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"训练数据不存在: {csv_path}")

    df = pd.read_csv(csv_path)
    _validate_training_df(df)

    for c in FEATURE_COLUMNS:
        df[c] = pd.to_numeric(df[c], errors="raise")
    df[LABEL_COLUMN] = pd.to_numeric(df[LABEL_COLUMN], errors="raise")

    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")

    return df


def train_model(csv_path, model_path, meta_path=None, cfg=None):
    cfg = cfg or ModelConfig()
    df = load_training_dataframe(csv_path)

    x = df[FEATURE_COLUMNS]
    y = df[LABEL_COLUMN]

    model = XGBRegressor(
        n_estimators=cfg.n_estimators,
        learning_rate=cfg.learning_rate,
        max_depth=cfg.max_depth,
        min_child_weight=cfg.min_child_weight,
        subsample=cfg.subsample,
        colsample_bytree=cfg.colsample_bytree,
        reg_alpha=cfg.reg_alpha,
        reg_lambda=cfg.reg_lambda,
        random_state=cfg.random_state,
        objective=cfg.objective,
        eval_metric=cfg.eval_metric,
        n_jobs=1,
    )
    model.fit(x, y)

    _ensure_parent_dir(model_path)
    model.save_model(model_path)

    if not meta_path:
        base, _ = os.path.splitext(model_path)
        meta_path = f"{base}.meta.json"

    meta = {
        "feature_columns": FEATURE_COLUMNS,
        "label_column": LABEL_COLUMN,
        "row_count": int(len(df)),
        "dish_count": int(df["dish_id"].nunique()) if "dish_id" in df.columns else None,
        "params": {
            "n_estimators": cfg.n_estimators,
            "learning_rate": cfg.learning_rate,
            "max_depth": cfg.max_depth,
            "min_child_weight": cfg.min_child_weight,
            "subsample": cfg.subsample,
            "colsample_bytree": cfg.colsample_bytree,
            "reg_alpha": cfg.reg_alpha,
            "reg_lambda": cfg.reg_lambda,
            "random_state": cfg.random_state,
            "objective": cfg.objective,
            "eval_metric": cfg.eval_metric,
            "n_jobs": 1,
        },
    }
    _ensure_parent_dir(meta_path)
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    print(f"[OK] 训练完成，样本数={len(df)}，模型已保存: {model_path}")
    print(f"[OK] 元信息已保存: {meta_path}")


def _build_feature_rows_for_date(
    target_date,
    weather_code,
    avg_temperature,
    window_1_online,
    window_2_online,
    window_3_online,
    special_event_code,
):
    dishes = Dish.query.filter_by(is_active=True).order_by(Dish.id.asc()).all()
    if not dishes:
        raise ValueError("当前没有可预测的在售菜品")

    dow = target_date.weekday()
    is_weekend = 1 if dow >= 5 else 0

    rows = []
    for d in dishes:
        rows.append(
            {
                "dish_id": d.id,
                "feature_day_of_week": dow,
                "feature_is_weekend": is_weekend,
                "feature_is_holiday": _to_int_bool(0),
                "feature_weather_code": int(weather_code),
                "feature_avg_temperature": float(avg_temperature),
                "feature_window_1_online": _to_int_bool(window_1_online),
                "feature_window_2_online": _to_int_bool(window_2_online),
                "feature_window_3_online": _to_int_bool(window_3_online),
                "feature_special_event_code": int(special_event_code),
            }
        )
    return rows


def predict_and_upsert(
    model_path,
    target_date,
    weather_code,
    avg_temperature,
    window_1_online=1,
    window_2_online=1,
    window_3_online=1,
    special_event_code=0,
    is_holiday=0,
    update_daily_menu_stock=False,
):
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"模型文件不存在: {model_path}")

    model = XGBRegressor()
    model.load_model(model_path)

    rows = _build_feature_rows_for_date(
        target_date=target_date,
        weather_code=weather_code,
        avg_temperature=avg_temperature,
        window_1_online=window_1_online,
        window_2_online=window_2_online,
        window_3_online=window_3_online,
        special_event_code=special_event_code,
    )

    for r in rows:
        r["feature_is_holiday"] = _to_int_bool(is_holiday)

    x_pred = pd.DataFrame(rows)[FEATURE_COLUMNS]
    y_pred = model.predict(x_pred)

    results = []
    for idx, row in enumerate(rows):
        qty = int(round(float(y_pred[idx])))
        if qty < 0:
            qty = 0

        pred = DishPrediction.query.filter_by(
            dish_id=row["dish_id"],
            date=target_date,
        ).first()

        if pred:
            pred.predicted_quantity = qty
            if pred.adjusted_quantity is None:
                pred.adjusted_quantity = qty
        else:
            pred = DishPrediction(
                dish_id=row["dish_id"],
                date=target_date,
                predicted_quantity=qty,
                adjusted_quantity=qty,
            )
            db.session.add(pred)

        if update_daily_menu_stock:
            menus = DailyMenu.query.filter_by(dish_id=row["dish_id"], date=target_date).all()
            for m in menus:
                m.stock = qty
                m.is_sold_out = qty <= 0

        results.append({
            "dish_id": row["dish_id"],
            "predicted_quantity": qty,
        })

    db.session.commit()
    print(f"[OK] 预测完成并写入数据库: {target_date.isoformat()}，菜品数={len(results)}")
    return results




def _data_dir():
    return os.path.join(BACKEND_DIR, "data")


def _default_model_path():
    return os.path.join(_data_dir(), "xgb_dish_sales_model.json")


def _default_training_csv_path():
    data_dir = _data_dir()
    candidates = [
        os.path.join(data_dir, name)
        for name in os.listdir(data_dir)
        if name.startswith("manual_sales_template_") and name.endswith(".csv")
    ]
    if not candidates:
        raise FileNotFoundError("未找到 manual_sales_template_*.csv 训练数据")
    candidates.sort()
    return candidates[-1]


def _get_config_value(key, default_value):
    cfg = SystemConfig.query.filter_by(key=key).first()
    if not cfg:
        return default_value
    return cfg.value


def run_training(app):
    with app.app_context():
        csv_path = _default_training_csv_path()
        model_path = _default_model_path()
        train_model(csv_path=csv_path, model_path=model_path)


def run_prediction(app):
    with app.app_context():
        model_path = _default_model_path()
        today = datetime.date.today()

        weather_code = int(_get_config_value("prediction_weather_code", 0))
        avg_temperature = float(_get_config_value("prediction_avg_temperature", 20))
        is_holiday = int(_get_config_value("prediction_is_holiday", 0))
        special_event_code = int(_get_config_value("prediction_special_event_code", 0))

        windows = Window.query.all()
        online_by_number = {w.window_number: 1 if w.is_online else 0 for w in windows}

        window_1_online = int(online_by_number.get(1, 1))
        window_2_online = int(online_by_number.get(2, 1))
        window_3_online = int(online_by_number.get(3, 1))

        predict_and_upsert(
            model_path=model_path,
            target_date=today,
            weather_code=weather_code,
            avg_temperature=avg_temperature,
            window_1_online=window_1_online,
            window_2_online=window_2_online,
            window_3_online=window_3_online,
            special_event_code=special_event_code,
            is_holiday=is_holiday,
            update_daily_menu_stock=True,
        )


def parse_date(value):
    return datetime.datetime.strptime(value, "%Y-%m-%d").date()


def build_cli():
    parser = argparse.ArgumentParser(description="食堂销量预测（XGBoost）")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_train = sub.add_parser("train", help="用CSV训练模型")
    p_train.add_argument("--csv", required=True, help="训练数据CSV路径")
    p_train.add_argument("--model", required=True, help="模型输出路径（建议 .json）")
    p_train.add_argument("--meta", default=None, help="元信息输出路径（可选）")

    p_predict = sub.add_parser("predict", help="按日期预测并入库")
    p_predict.add_argument("--model", required=True, help="模型路径")
    p_predict.add_argument("--date", required=True, help="预测日期，格式 YYYY-MM-DD")
    p_predict.add_argument("--weather-code", type=int, required=True, help="天气编码：0晴/1阴/2雨")
    p_predict.add_argument("--avg-temperature", type=float, required=True, help="平均温度")
    p_predict.add_argument("--is-holiday", type=int, default=0, help="是否节假日：0/1")
    p_predict.add_argument("--window-1-online", type=int, default=1, help="窗口1是否在线：0/1")
    p_predict.add_argument("--window-2-online", type=int, default=1, help="窗口2是否在线：0/1")
    p_predict.add_argument("--window-3-online", type=int, default=1, help="窗口3是否在线：0/1")
    p_predict.add_argument("--special-event-code", type=int, default=0, help="特殊事件编码：0无")
    p_predict.add_argument(
        "--update-daily-menu-stock",
        action="store_true",
        help="同时更新 DailyMenu.stock",
    )

    return parser


def main():
    parser = build_cli()
    args = parser.parse_args()

    if args.cmd == "train":
        train_model(
            csv_path=args.csv,
            model_path=args.model,
            meta_path=args.meta,
        )
        return

    if args.cmd == "predict":
        from app import create_app
        app = create_app()
        with app.app_context():
            results = predict_and_upsert(
                model_path=args.model,
                target_date=parse_date(args.date),
                weather_code=args.weather_code,
                avg_temperature=args.avg_temperature,
                is_holiday=args.is_holiday,
                window_1_online=args.window_1_online,
                window_2_online=args.window_2_online,
                window_3_online=args.window_3_online,
                special_event_code=args.special_event_code,
                update_daily_menu_stock=args.update_daily_menu_stock,
            )
            print(json.dumps(results, ensure_ascii=False, indent=2))
        return

    raise ValueError("未知命令")


if __name__ == "__main__":
    main()
