from fastapi import APIRouter

router = APIRouter(tags=["channel"], prefix="/channel")

# GET Channel total viewcount
# GET Channel subscribers
# POST Upload video
# PATCH Rename channel
# DELETE Delete video
#
# OLAP: Total revenue from monthly paid subscriptions
# OLAP: Strike count for channel, excluding the ones that have been expired.
# NOTE: may be too easy? ^
