from flask import Blueprint, jsonify, session, current_app

from 软件综合实训.final_canteen.backend.utils.predict_algo import run_prediction, run_training

prediction_bp = Blueprint('prediction_bp', __name__)


def _require_admin():
    if not session.get('admin_username'):
        return jsonify(success=False, error='未授权，请先登录'), 401
    return None


@prediction_bp.route('/prediction/run', methods=['POST'])
def manual_run_prediction():
    err = _require_admin()
    if err:
        return err

    try:
        run_prediction(current_app._get_current_object())
        return jsonify(success=True, data={'message': '预测执行完成'})
    except FileNotFoundError as e:
        return jsonify(success=False, error=str(e)), 400
    except ValueError as e:
        return jsonify(success=False, error=str(e)), 400


@prediction_bp.route('/prediction/train', methods=['POST'])
def manual_run_training():
    err = _require_admin()
    if err:
        return err

    try:
        run_training(current_app._get_current_object())
        return jsonify(success=True, data={'message': '模型训练完成'})
    except FileNotFoundError as e:
        return jsonify(success=False, error=str(e)), 400
    except ValueError as e:
        return jsonify(success=False, error=str(e)), 400
