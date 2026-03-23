from app.database import fetch_one, fetch_all
import uuid

async def save_chat(user_id: str, query: str, query_type: str, ensemble_response: str, 
                    medgemma_response: str | None, meditron_response: str | None, 
                    medichat_response: str | None, confidence: float):
    sql = """
    INSERT INTO chats (user_id, query, query_type, ensemble_response, 
                       medgemma_response, meditron_response, medichat_response, 
                       confidence, created_at)
    VALUES ($1::uuid, $2, $3, $4, $5, $6, $7, $8, NOW())
    RETURNING id
    """
    await fetch_one(sql, user_id, query, query_type, ensemble_response, 
                    medgemma_response, meditron_response, medichat_response, confidence)

async def get_chat_history(user_id: str, limit: int = 20, offset: int = 0):
    sql = """
    SELECT * FROM chats 
    WHERE user_id = $1 
    ORDER BY created_at DESC 
    LIMIT $2 OFFSET $3
    """
    records = await fetch_all(sql, user_id, limit, offset)
    return [dict(record) for record in records]
