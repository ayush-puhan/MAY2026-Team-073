from flask import Blueprint, request, g
from flask_restful import Api, Resource
from sqlalchemy import func

from app.database.database import get_session
from app.database.models import (RewardTask,RewardTaskCompletion,RewardPointsLedger,RewardStoreItem,RewardRedemption)
from app.database.enums import RedemptionStatus
from app.middleware.auth_middleware import require_auth

rewards_bp = Blueprint("rewards", __name__)
api = Api(rewards_bp)

def serialize_task(task):
    return {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "points": task.points,
        "type": task.type,
        "icon": task.icon,
        "category": task.category,
        "is_active": bool(task.is_active),
        "max_completions": task.max_completions,
        "requires_verified": bool(task.requires_verified)
    }


def serialize_completion(c):
    return {
        "id": c.id,
        "user_id": c.user_id,
        "task_id": c.task_id,
        "completed_at": c.completed_at.isoformat()
    }


def serialize_store_item(item):
    return {
        "id": item.id,
        "name": item.name,
        "description": item.description,
        "points_cost": item.points_cost,
        "category": item.category,
        "icon": item.icon,
        "stock": item.stock,
        "max_per_user": item.max_per_user,
        "is_active": bool(item.is_active),
        "requires_verified": bool(item.requires_verified)
    }


def serialize_ledger(entry):
    return {
        "id": entry.id,
        "points": entry.points,
        "reason": entry.reason,
        "source_event_id": entry.source_event_id,
        "created_at": entry.created_at.isoformat()
    }


def serialize_redemption(r):
    return {
        "id": r.id,
        "points_spent": r.points_spent,
        "reward_description": r.reward_description,
        "status": r.status.value,
        "approved_by": r.approved_by,
        "created_at": r.created_at.isoformat()
    }

class RewardTaskListResource(Resource):

    @require_auth
    def get(self):
        try:
            with get_session() as db:
                tasks = (
                    db.query(RewardTask)
                    .filter(RewardTask.is_active == 1)
                    .all()
                )

                return [serialize_task(t) for t in tasks], 200
        except Exception as e:
            return {'message'  :  f"Error  :  {e}"}, 500

class RewardTaskCompletionResource(Resource):

    @require_auth
    def get(self, user_id):
        try:
            with get_session() as db:

                completions = (
                    db.query(RewardTaskCompletion)
                    .filter(RewardTaskCompletion.user_id == user_id)
                    .all()
                )

                return [serialize_completion(c) for c in completions], 200
        except Exception as e:
            return {'message'  :  f"Error  :  {e}"}, 500

class CompleteRewardTaskResource(Resource):

    @require_auth
    def post(self):
        try:
            data = request.get_json()

            user_id = g.current_user.id
            task_id = data["task_id"]

            with get_session() as db:

                task = db.get(RewardTask, task_id)

                if not task:
                    return {"message": "Task not found"}, 404

                count = (
                    db.query(RewardTaskCompletion)
                    .filter_by(user_id=user_id, task_id=task_id)
                    .count()
                )

                if count >= task.max_completions:
                    return {
                        "message": "Task completion limit reached"
                    }, 400

                completion = RewardTaskCompletion(
                    user_id=user_id,
                    task_id=task_id
                )

                ledger = RewardPointsLedger(
                    user_id=user_id,
                    points=task.points,
                    reason=f"Completed task: {task.title}"
                )

                db.add(completion)
                db.add(ledger)
                db.commit()

                return {
                    "success": True,
                    "points_earned": task.points
                }, 201
        except Exception as e:
            return {'message'  :  f"Error  :  {e}"}, 500

class UserRewardPointsResource(Resource):

    @require_auth
    def get(self, user_id):
        try:
            with get_session() as db:

                total = (
                    db.query(func.coalesce(func.sum(RewardPointsLedger.points), 0))
                    .filter(RewardPointsLedger.user_id == user_id)
                    .scalar()
                )

                redeemed = (
                    db.query(func.coalesce(func.sum(RewardRedemption.points_spent), 0))
                    .filter(RewardRedemption.user_id == user_id)
                    .scalar()
                )

                return {
                    "balance": total - redeemed,
                    "total_points": total,
                    "redeemed_points": redeemed
                }, 200
        except Exception as e:
            return {'message'  :  f"Error  :  {e}"}, 500

class RewardLedgerResource(Resource):

    @require_auth
    def get(self, user_id):
        try:
            with get_session() as db:

                entries = (
                    db.query(RewardPointsLedger)
                    .filter_by(user_id=user_id)
                    .order_by(RewardPointsLedger.created_at.desc())
                    .all()
                )

                return [serialize_ledger(e) for e in entries], 200
        except Exception as e:
            return {'message'  :  f"Error  :  {e}"}, 500

class RewardStoreItemsResource(Resource):

    @require_auth
    def get(self):
        try:
            with get_session() as db:

                items = (
                    db.query(RewardStoreItem)
                    .filter(
                        RewardStoreItem.is_active == 1,
                        RewardStoreItem.stock > 0
                    )
                    .all()
                )

                return [serialize_store_item(i) for i in items], 200
        except Exception as e:
            return {'message'  :  f"Error  :  {e}"}, 500

class RedeemRewardResource(Resource):

    @require_auth
    def post(self):
        try:
            data = request.get_json()

            user_id = g.current_user.id
            item_id = data["item_id"]

            with get_session() as db:

                item = db.get(RewardStoreItem, item_id)

                if not item:
                    return {"message": "Reward not found"}, 404

                if item.stock <= 0:
                    return {"message": "Out of stock"}, 400

                earned = (
                    db.query(func.coalesce(func.sum(RewardPointsLedger.points), 0))
                    .filter(RewardPointsLedger.user_id == user_id)
                    .scalar()
                )

                spent = (
                    db.query(func.coalesce(func.sum(RewardRedemption.points_spent), 0))
                    .filter(RewardRedemption.user_id == user_id)
                    .scalar()
                )

                available = earned - spent

                if available < item.points_cost:
                    return {
                        "message": "Insufficient reward points"
                    }, 400

                redemption = RewardRedemption(
                    user_id=user_id,
                    points_spent=item.points_cost,
                    reward_description=item.name,
                    status=RedemptionStatus.REQUESTED
                )

                item.stock -= 1

                db.add(redemption)
                db.commit()

                return {
                    "success": True,
                    "message": "Reward redeemed successfully"
                }, 201
        except Exception as e:
            return {'message'  :  f"Error  :  {e}"}, 500

class RewardRedemptionHistoryResource(Resource):

    @require_auth
    def get(self, user_id):
        try:
            with get_session() as db:

                redemptions = (
                    db.query(RewardRedemption)
                    .filter_by(user_id=user_id)
                    .order_by(RewardRedemption.created_at.desc())
                    .all()
                )

                return [serialize_redemption(r) for r in redemptions], 200
        except Exception as e:
            return {'messge' : 'Uncaught Error'}, 500

api.add_resource(
    RewardTaskListResource,
    "/tasks"
)

api.add_resource(
    RewardTaskCompletionResource,
    "/tasks/completions/<int:user_id>"
)

api.add_resource(
    CompleteRewardTaskResource,
    "/tasks/complete"
)

api.add_resource(
    UserRewardPointsResource,
    "/points/<int:user_id>"
)

api.add_resource(
    RewardLedgerResource,
    "/ledger/<int:user_id>"
)

api.add_resource(
    RewardStoreItemsResource,
    "/store/items"
)

api.add_resource(
    RedeemRewardResource,
    "/store/redeem"
)

api.add_resource(
    RewardRedemptionHistoryResource,
    "/redemptions/<int:user_id>"
)