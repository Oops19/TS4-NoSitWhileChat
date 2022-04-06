#
# LICENSE https://tos.ea.com/legalapp/WEBTERMS/US/en/PC/
# Idea and initial code © 2020 TAESimmer https://modthesims.info/m/10223632 - https://modthesims.info/d/643777/no-autonomous-sitting-while-talking.html
# Fix © 2022 ColonolNutty https://www.patreon.com/colonolnutty
# Sharing is caring © 2022 o19 https://github.com/Oops19
#
#


import services
import sims4
from interactions.context import InteractionSource

from no_sit_while_chat.modinfo import ModInfo


from sims.sim import Sim
from sims.sim_info import SimInfo
from sims4.resources import get_resource_key

from sims4communitylib.enums.interactions_enum import CommonInteractionId
from sims4communitylib.events.event_handling.common_event_registry import CommonEventRegistry
from sims4communitylib.events.interaction.events.interaction_queued import S4CLInteractionQueuedEvent
from sims4communitylib.events.zone_spin.common_zone_spin_event_dispatcher import CommonZoneSpinEventDispatcher
from sims4communitylib.services.commands.common_console_command import CommonConsoleCommand
from sims4communitylib.services.commands.common_console_command_output import CommonConsoleCommandOutput
from sims4communitylib.utils.common_injection_utils import CommonInjectionUtils
from sims4communitylib.utils.common_log_registry import CommonLog, CommonLogRegistry, CommonMessageType
from sims4communitylib.utils.sims.common_sim_interaction_utils import CommonSimInteractionUtils
from sims4communitylib.utils.sims.common_sim_utils import CommonSimUtils


log: CommonLog = CommonLogRegistry.get().register_log(f"{ModInfo.get_identity().name}", ModInfo.get_identity().name)
log.enable()
log.debug(f"Starting {ModInfo.get_identity().name} v{ModInfo.get_identity().version} ")
log.info(f"Use 'no_sit.toggle' to 'Toggle the No Sit While Chatting mod on or off.'")
log.info(f"Use 'no_sit.status' to 'Check the status of the No Sit While Chatting mod.'")
log.disable()


class NoSitWhileChattingMod:
    """A class used for storing variables."""
    NO_SIT_ALLOWED = True
    instance_manager = None

    def __init__(self):
        _manager = "INTERACTION"
        NoSitWhileChattingMod.instance_manager = services.get_instance_manager(sims4.resources.Types[_manager])
        if not NoSitWhileChattingMod.instance_manager:
            log.error("instance_manager == None")

    @classmethod
    def is_chatting(cls, sim_info: SimInfo) -> bool:
        """Whether or not the Sim is chatting."""
        # sim_Toddler_Talk
        toddler_talk = 140885
        return CommonSimInteractionUtils.has_interactions_running_or_queued(sim_info, (CommonInteractionId.SIM_CHAT, toddler_talk))


@CommonInjectionUtils.inject_safely_into(ModInfo.get_identity(), Sim, Sim.in_non_adjustable_posture.__name__)
def o19_in_non_adjustable_posture(original, self, *_, **__) -> bool:
    sim_info = CommonSimUtils.get_sim_info(self)

    if log.is_enabled(CommonMessageType.DEBUG):
        log.debug(f"{sim_info}: standing={CommonSimInteractionUtils.is_standing(sim_info)} sitting={CommonSimInteractionUtils.is_sitting(sim_info)} chatting={NoSitWhileChattingMod.is_chatting(sim_info)}")

    if CommonSimInteractionUtils.is_standing(sim_info):
        if NoSitWhileChattingMod.is_chatting(sim_info):
            return False
    return original(self, *_, **__)


@CommonEventRegistry.handle_events(ModInfo.get_identity())
def handle_events__interaction_queued_event(event_data: S4CLInteractionQueuedEvent):
    bubble_event = True
    if NoSitWhileChattingMod.NO_SIT_ALLOWED:
        if CommonZoneSpinEventDispatcher().game_loaded:
            if event_data.interaction.source == InteractionSource.SOCIAL_ADJUSTMENT:
                if NoSitWhileChattingMod.is_chatting(event_data.queuing_sim_info):
                    bubble_event = False

    if log.is_enabled(CommonMessageType.DEBUG):
        if not NoSitWhileChattingMod.instance_manager:
            NoSitWhileChattingMod.instance_manager = services.get_instance_manager(sims4.resources.Types["INTERACTION"])
        log.debug(f"{event_data.interaction_queue.sim.sim_id} '{event_data.interaction_queue.sim.sim_info}' - {event_data.interaction.source} - {event_data.interaction.guid64} '{NoSitWhileChattingMod.instance_manager.get(event_data.interaction.guid64)}'")

    return bubble_event


@CommonConsoleCommand(ModInfo.get_identity(), 'no_sit.toggle', 'Toggle the No Sit While Chatting mod on or off.')
def _no_sit_toggle(output: CommonConsoleCommandOutput):
    NoSitWhileChattingMod.NO_SIT_ALLOWED = not NoSitWhileChattingMod.NO_SIT_ALLOWED
    if NoSitWhileChattingMod.NO_SIT_ALLOWED:
        output('NoSitWhileChatting has been enabled!')
    else:
        output('NoSitWhileChatting has been disabled!')


@CommonConsoleCommand(ModInfo.get_identity(), 'no_sit.status', 'Check the status of the No Sit While Chatting mod.')
def _no_sit_check(output: CommonConsoleCommandOutput):
    if NoSitWhileChattingMod.NO_SIT_ALLOWED:
        output('NoSitWhileChatting is currently enabled.')
    else:
        output('NoSitWhileChatting is currently disabled.')
