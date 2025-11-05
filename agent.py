import logging
import os

from dotenv import load_dotenv
from prompts import AGENT_INSTRUCTION, SESSION_INSTRUCTION
from livekit.agents import(
    Agent,
    AgentSession,
    JobContext,
    RoomOutputOptions,
    WorkerOptions,
    WorkerType,
    cli,
)
from livekit.plugins import openai, tavus, deepgram, rime

logger=logging.getLogger("tavus-avatar-example")
logger.setLevel(logging.INFO)

load_dotenv()

async def entrypoint(ctx: JobContext):
    await ctx.connect()

    session = AgentSession(
        llm=openai.LLM(model="gpt-4o-mini"),
        stt=deepgram.STT(model="nova-3"),
        tts=rime.TTS(
            model="mistv2",
            speaker="grove",
            speed_alpha=1.1,
            reduce_latency=True,
        ),
    )

    persona_id=os.getenv("TAVUS_PERSONA_ID")
    replica_id=os.getenv("TAVUS_REPLICA_ID")

    tavus_avatar=tavus.AvatarSession(persona_id=persona_id, replica_id=replica_id)
    await tavus_avatar.start(session, room=ctx.room)

    await session.start(
        agent=Agent(instructions=AGENT_INSTRUCTION),  # Use prompt variable for agent
        room=ctx.room,
        room_output_options=RoomOutputOptions(audio_enabled=False),
    )

    await session.generate_reply(instructions=SESSION_INSTRUCTION)  # Session instructions

if __name__=="__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, worker_type=WorkerType.ROOM))
