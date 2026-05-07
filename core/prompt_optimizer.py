import config
from groq import Groq

def optimize_prompt(user_prompt: str, room_type: str, style: str) -> str:
    """Use Groq LLM to enhance a vague room description into a detailed image generation prompt."""
    if not config.GROQ_API_KEY:
        return user_prompt

    system = (
        "You are an expert interior design prompt engineer. "
        "Convert the user's room description into a highly detailed, photorealistic image generation prompt. "
        "Include lighting, materials, camera angle, and mood. Return only the enhanced prompt, nothing else."
    )
    user_msg = f"Room type: {room_type}\nStyle: {style}\nDescription: {user_prompt}"

    try:
        client = Groq(api_key=config.GROQ_API_KEY)
        response = client.chat.completions.create(
            model=config.GROQ_MODEL,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user_msg}
            ],
            max_tokens=300,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"[prompt_optimizer] Groq error: {e}")
        return user_prompt