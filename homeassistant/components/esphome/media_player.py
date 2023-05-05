"""Support for ESPHome media players."""
from __future__ import annotations

from typing import Any

from aioesphomeapi import (
    MediaPlayerCommand,
    MediaPlayerEntityState,
    MediaPlayerInfo,
    MediaPlayerState as EspMediaPlayerState,
    MediaPlayerRepeatMode as EspRepeatMode
)

from homeassistant.components import media_source
from homeassistant.components.media_player import (
    BrowseMedia,
    MediaPlayerDeviceClass,
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
    MediaType,
    async_process_play_media_url,
    RepeatMode
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import EsphomeEntity, esphome_state_property, platform_async_setup_entry
from .enum_mapper import EsphomeEnumMapper


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up esphome media players based on a config entry."""
    await platform_async_setup_entry(
        hass,
        entry,
        async_add_entities,
        component_key="media_player",
        info_type=MediaPlayerInfo,
        entity_type=EsphomeMediaPlayer,
        state_type=MediaPlayerEntityState,
    )


_STATES: EsphomeEnumMapper[EspMediaPlayerState, MediaPlayerState] = EsphomeEnumMapper(
    {
        EspMediaPlayerState.IDLE: MediaPlayerState.IDLE,
        EspMediaPlayerState.PLAYING: MediaPlayerState.PLAYING,
        EspMediaPlayerState.PAUSED: MediaPlayerState.PAUSED,
        EspMediaPlayerState.ON: MediaPlayerState.ON,
        EspMediaPlayerState.OFF: MediaPlayerState.OFF,
        EspMediaPlayerState.STANDBY: MediaPlayerState.STANDBY,
        EspMediaPlayerState.BUFFERING: MediaPlayerState.BUFFERING
    }
)

_REPEAT_MODES: EsphomeEnumMapper[EspRepeatMode, RepeatMode] = EsphomeEnumMapper(
    {
        EspRepeatMode.OFF: RepeatMode.OFF,
        EspRepeatMode.ONE: RepeatMode.ONE,
        EspRepeatMode.ALL: RepeatMode.ALL
    }
)


class EsphomeMediaPlayer(
    EsphomeEntity[MediaPlayerInfo, MediaPlayerEntityState], MediaPlayerEntity
):
    """A media player implementation for esphome."""

    _attr_device_class = MediaPlayerDeviceClass.SPEAKER

    @property
    @esphome_state_property
    def state(self) -> MediaPlayerState | None:
        """Return current state."""
        return _STATES.from_esphome(self._state.state)

    @property
    @esphome_state_property
    def volume_level(self) -> float | None:
        """Volume level of the media player (0..1)."""
        return self._state.volume

    @property
    @esphome_state_property
    def is_volume_muted(self) -> bool:
        """Return true if volume is muted."""
        return self._state.muted

    @property
    @esphome_state_property
    def source(self) -> str | None:
        """Volume level of the media player (0..1)."""
        return self._state.source

    @property
    @esphome_state_property
    def source_list(self) -> list[str] | None:
        """Volume level of the media player (0..1)."""
        return self._state.source_list

    @property
    @esphome_state_property
    def sound_mode(self) -> str | None:
        """Volume level of the media player (0..1)."""
        return self._state.sound_mode

    @property
    @esphome_state_property
    def sound_mode_list(self) -> list[str] | None:
        """Volume level of the media player (0..1)."""
        return self._state.sound_mode_list

    @property
    @esphome_state_property
    def repeat(self) -> RepeatMode | str | None:
        """Volume level of the media player (0..1)."""
        return _REPEAT_MODES.from_esphome(self._state.repeat_mode)

    @property
    def supported_features(self) -> MediaPlayerEntityFeature:
        """Flag supported features."""
        flags = 0

        if self._static_info.supports_pause:
            flags |= MediaPlayerEntityFeature.PAUSE
        if self._static_info.supports_seek:
            flags |= MediaPlayerEntityFeature.SEEK
        if self._static_info.supports_volume_set:
            flags |= MediaPlayerEntityFeature.VOLUME_SET
        if self._static_info.supports_volume_mute:
            flags |= MediaPlayerEntityFeature.VOLUME_MUTE
        if self._static_info.supports_previous_track:
            flags |= MediaPlayerEntityFeature.PREVIOUS_TRACK
        if self._static_info.supports_next_track:
            flags |= MediaPlayerEntityFeature.NEXT_TRACK
        if self._static_info.supports_turn_on:
            flags |= MediaPlayerEntityFeature.TURN_ON
        if self._static_info.supports_turn_off:
            flags |= MediaPlayerEntityFeature.TURN_OFF
        if self._static_info.supports_play_media:
            flags |= MediaPlayerEntityFeature.PLAY_MEDIA | MediaPlayerEntityFeature.BROWSE_MEDIA
        if self._static_info.supports_volume_step:
            flags |= MediaPlayerEntityFeature.VOLUME_STEP
        if self._static_info.supports_select_source:
            flags |= MediaPlayerEntityFeature.SELECT_SOURCE
        if self._static_info.supports_stop:
            flags |= MediaPlayerEntityFeature.STOP
        if self._static_info.supports_clear_playlist:
            flags |= MediaPlayerEntityFeature.CLEAR_PLAYLIST
        if self._static_info.supports_play:
            flags |= MediaPlayerEntityFeature.PLAY
        if self._static_info.supports_shuffle_set:
            flags |= MediaPlayerEntityFeature.SHUFFLE_SET
        if self._static_info.supports_select_sound_mode:
            flags |= MediaPlayerEntityFeature.SELECT_SOUND_MODE
        if self._static_info.supports_repeat_set:
            flags |= MediaPlayerEntityFeature.REPEAT_SET

        return flags

    async def async_media_pause(self) -> None:
        """Send pause command."""
        await self._client.media_player_command(
            self._static_info.key,
            command=MediaPlayerCommand.PAUSE,
        )

    async def async_media_seek(self, position: float) -> None:
        """Send pause command."""
        await self._client.media_player_command(
            self._static_info.key,
            command=MediaPlayerCommand.SEEK,
            seek_position=position
        )

    async def async_set_volume_level(self, volume: float) -> None:
        """Set volume level, range 0..1."""
        await self._client.media_player_command(
            self._static_info.key,
            command=MediaPlayerCommand.VOLUME_SET,
            volume_level=volume,
        )

    async def async_mute_volume(self, mute: bool) -> None:
        """Mute the volume."""
        await self._client.media_player_command(
            self._static_info.key,
            command=MediaPlayerCommand.MUTE if mute else MediaPlayerCommand.UNMUTE,
        )

    async def async_media_previous_track(self) -> None:
        """Send pause command."""
        await self._client.media_player_command(
            self._static_info.key,
            command=MediaPlayerCommand.PREVIOUS_TRACK,
        )

    async def async_media_next_track(self) -> None:
        """Send pause command."""
        await self._client.media_player_command(
            self._static_info.key,
            command=MediaPlayerCommand.NEXT_TRACK,
        )

    async def async_turn_on(self) -> None:
        await self._client.media_player_command(
            self._static_info.key,
            command=MediaPlayerCommand.TURN_ON
        )

    async def async_turn_off(self) -> None:
        await self._client.media_player_command(
            self._static_info.key,
            command=MediaPlayerCommand.TURN_OFF
        )

    async def async_play_media(
        self, media_type: MediaType | str, media_id: str, **kwargs: Any
    ) -> None:
        """Send the play command with media url to the media player."""
        if media_source.is_media_source_id(media_id):
            sourced_media = await media_source.async_resolve_media(
                self.hass, media_id, self.entity_id
            )
            media_id = sourced_media.url

        media_id = async_process_play_media_url(self.hass, media_id)

        await self._client.media_player_command(
            self._static_info.key,
            media_url=media_id,
        )

    async def async_browse_media(
        self,
        media_content_type: MediaType | str | None = None,
        media_content_id: str | None = None,
    ) -> BrowseMedia:
        """Implement the websocket media browsing helper."""
        return await media_source.async_browse_media(
            self.hass,
            media_content_id,
            content_filter=lambda item: item.media_content_type.startswith("audio/"),
        )

    async def async_volume_up(self) -> None:
        """Send stop command."""
        await self._client.media_player_command(
            self._static_info.key,
            command=MediaPlayerCommand.VOLUME_UP,
        )

    async def async_volume_down(self) -> None:
        """Send stop command."""
        await self._client.media_player_command(
            self._static_info.key,
            command=MediaPlayerCommand.VOLUME_DOWN,
        )

    async def async_select_source(self, source: str) -> None:
        """Send stop command."""
        await self._client.media_player_command(
            self._static_info.key,
            command=MediaPlayerCommand.SELECT_SOURCE,
            source=source
        )

    async def async_media_stop(self) -> None:
        """Send stop command."""
        await self._client.media_player_command(
            self._static_info.key,
            command=MediaPlayerCommand.STOP,
        )

    async def async_clear_playlist(self) -> None:
        """Send stop command."""
        await self._client.media_player_command(
            self._static_info.key,
            command=MediaPlayerCommand.CLEAR_PLAYLIST,
        )

    async def async_media_play(self) -> None:
        """Send play command."""
        await self._client.media_player_command(
            self._static_info.key,
            command=MediaPlayerCommand.PLAY,
        )

    async def async_set_shuffle(self, shuffle: bool) -> None:
        """Send play command."""
        await self._client.media_player_command(
            self._static_info.key,
            command=MediaPlayerCommand.SHUFFLE_SET,
            shuffle_set=shuffle
        )

    async def async_select_sound_mode(self, sound_mode: str) -> None:
        """Send play command."""
        await self._client.media_player_command(
            self._static_info.key,
            command=MediaPlayerCommand.SELECT_SOUND_MODE,
            sound_mode=sound_mode
        )

    async def async_set_repeat(self, repeat: RepeatMode) -> None:
        """Send play command."""
        await self._client.media_player_command(
            self._static_info.key,
            command=MediaPlayerCommand.SELECT_SOUND_MODE,
            repeat=_REPEAT_MODES.from_hass(repeat)
        )
