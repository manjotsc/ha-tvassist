<p align="center">
  <img src="custom_components/tv_assist/icons/icon.png" width="120" alt="TV Assist logo" />
</p>

<h1 align="center">TV Assist for Home Assistant</h1>

<p align="center">
  Push rich toast/banner notifications, persistent status pills, and text-to-speech to any
  Android&nbsp;TV running the <strong>TV Assist</strong> app — over your local network, no cloud.
</p>

<p align="center">
  <a href="https://github.com/hacs/integration"><img src="https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge" alt="HACS Custom" /></a>
  <a href="https://github.com/manjotsc/tv-assist-ha/releases"><img src="https://img.shields.io/github/v/release/manjotsc/tv-assist-ha?style=for-the-badge" alt="Release" /></a>
  <img src="https://img.shields.io/badge/Home%20Assistant-2024.1%2B-41BDF5.svg?style=for-the-badge&logo=home-assistant&logoColor=white" alt="Home Assistant 2024.1+" />
  <img src="https://img.shields.io/badge/iot__class-local__push-2ea44f.svg?style=for-the-badge" alt="Local push" />
</p>

<p align="center">
  <a href="https://github.com/manjotsc/tv-assist-ha/actions/workflows/hassfest.yml"><img src="https://github.com/manjotsc/tv-assist-ha/actions/workflows/hassfest.yml/badge.svg" alt="Validate with hassfest" /></a>
  <a href="https://github.com/manjotsc/tv-assist-ha/actions/workflows/validate.yml"><img src="https://github.com/manjotsc/tv-assist-ha/actions/workflows/validate.yml/badge.svg" alt="HACS validation" /></a>
</p>

---

Each TV running **TV Assist** (Settings → Notifications → Enable) is added as a **device**. The
integration registers five actions — `tv_assist.notify`, `tv_assist.persistent`, `tv_assist.clear`,
`tv_assist.speak`, and `tv_assist.play_sound` — that you target by picking a TV from a **dropdown**.

## ✨ Features

- 🔔 **Rich notifications** — title, message, source line, MDI/Iconify/URL icons, custom colors, corner + size.
- 📌 **Persistent pills** — pin compact status chips (icon + text) to a corner; update or clear them by `id`.
- 🖼️ **Camera & media** — show a camera snapshot, a live camera stream, or any image/video URL on screen.
- 🗣️ **Text-to-speech** — announce messages through the TV speakers, with audio ducking and queueing.
- 🔊 **Play sounds** — chimes / MP3 / WAV through the TV, with looping and volume control.
- ⚡ **Flash & attention** — pulse a pill's icon or border to grab attention until dismissed.
- 🕗 **On-screen display** — remotely control the TV's dimming layer and always-on clock.
- 🏠 **100% local push** — direct LAN calls to the TV; no cloud, no account, low latency.

## 📦 Installation

### HACS (recommended)

[![Open your Home Assistant instance and open this repository inside HACS.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=manjotsc&repository=tv-assist-ha&category=integration)

1. In HACS, open the **⋮** menu → **Custom repositories**.
2. Add `https://github.com/manjotsc/tv-assist-ha` with category **Integration**.
3. Search for **TV Assist**, install it, then **restart Home Assistant**.

<details>
<summary><b>Manual installation</b></summary>

1. Copy `custom_components/tv_assist/` into your Home Assistant config:
   `…/config/custom_components/tv_assist/`
2. Restart Home Assistant.

</details>

### Add your TVs

1. **Settings → Devices & Services → Add Integration → “TV Assist”.**
2. Enter a **Name** (e.g. `Bedroom TV`), the **IP / port** shown in the TV app
   (Settings → Notifications → *Server address*), and optionally a **stable identifier**
   (e.g. `bedroom_tv`). Repeat for each TV.

> [!NOTE]
> On the TV: enable **Settings → Notifications**, grant the **overlay** permission, and keep
> **Run in background** on so it's always listening.

## 🎯 Targeting a TV

Every action accepts **one** of three ways to pick the TV:

| Field | What it is | Best for |
| --- | --- | --- |
| `device_id` | The device **dropdown** | Quick manual calls (changes if you re-add the integration) |
| `target` | The stable identifier you set (e.g. `bedroom_tv`) | Automations |
| `host` | A manual `host:port` | A TV that isn't added |

> [!TIP]
> Omit all three to broadcast to **every** added TV.

## 🔔 Send a notification

```yaml
action: tv_assist.notify
data:
  device_id: abc123…        # or: target: bedroom_tv   (chosen from the dropdown)
  source: "Home Assistant"  # small grey line above the title
  title: "Front door"
  message: "Someone's at the door"
  icon: "mdi:doorbell"      # MDI/Iconify name, an SVG/PNG/JPG URL, or an entity_picture (avatar)
  small_icon: "mdi:home"    # small badge on the icon's corner
  color: "#F39C12"          # border color of the card (also: border_color); empty = no border
  icon_color: "#FFFFFF"     # also: small_icon_color / title_color / source_color / message_color
  background_color: "#1E2228" # a hex (#AARRGGBB ok), or "transparent"
  icon_background: "#22FFFFFF"   # also: small_icon_background
  duration: 8               # seconds; 0 = persistent (stays until cleared)
  position: "top-right"     # top-left | top-center | top-right | bottom-left | bottom-center | bottom-right
  size: "medium"            # small | medium | large
  camera: "camera.front_door"        # camera entity → the TV fetches a still snapshot
  # camera_stream: "camera.front_door" # camera entity → the TV plays its live stream (video)
  # image: "http://…/snap.jpg"       # …or a direct image URL
  # media_url: "rtsp://…/stream"     # image OR a video/stream (rtsp/hls/dash); type auto-detected
  id: "doorbell"            # optional; reuse to replace / to clear
```

A notification can also voice itself through TTS — set `speak_mode` on `tv_assist.notify`: `default` uses
this TV's **Audio & announcements** default, or override per push with `both` ("Title. Message"),
`separate` (title, then message), `message`, or `title`. Picking any mode turns speech on. (The legacy
`speak: true` — "voice it with the TV's default mode" — is still accepted.)

By default the speech is read once and a `sound:` file plays once. Set `speak_repeat: loop` and/or
`sound_repeat: loop` to keep repeating until the notification leaves the screen (auto-expiry, dismiss,
replace, or clear). A pinned notification (`duration: 0`) is capped at 60s so it can't play forever.
Repeated speech waits for the current read to finish, then pauses `speak_repeat_gap` seconds (default
2, from the TV's Audio settings) before repeating — so it never overlaps or races.

## 📌 Persistent pills

Pin a small persistent pill (icon + optional text) to a corner — several line up in a row, like a
status bar. Reuse the `id` to update it; remove it with `tv_assist.clear` (or `visible: false`).

```yaml
action: tv_assist.persistent
data:
  target: bedroom_tv
  id: battery               # required — reuse to update / clear
  icon: "mdi:battery-70"
  message: "88%"            # optional text next to the icon
  shape: rounded            # rounded | circle | rectangular
  icon_color: "#FFC107"
  background_color: "#1E2228" # hex / rgb() / name / transparent
  position: top-right
  # --- Flash / attention (icon & border independent; set a color to pulse that element) ---
  # flash_icon_color: "#FF5252"    # pulse the icon this color
  # flash_border_color: "#FF5252"  # pulse the border this color
  # flash_icon_type: blink         # pulse | blink | glow  (per-element style)
  # flash_border_type: pulse       # pulse | blink | glow
  # flash_icon_speed: 300          # ms per cycle (lower = faster); blink shows speed best
  # flash_border_speed: 1200       # ms per cycle for the border (independent of the icon)
  # expiration: 3600         # optional auto-remove after N seconds
```

Persistent pills support the same audio as notifications — `sound`, `volume`, `duck`, `language`,
`speak_repeat`, `sound_repeat`. For speech, `speak` is a single choice: `text` voices the pill's
label + message, or `custom` voices the separate `speak_text` field (handy when a pill shows something
terse like `88%` but should say "Battery is at 88 percent"); leave `speak` unset for silent.

## 🗣️ Speak (text-to-speech)

Announce text through the TV speakers. By default it ducks the current TV audio while speaking.

```yaml
action: tv_assist.speak
data:
  target: bedroom_tv
  message: "The front door is unlocked"
  # language: en-US    # BCP-47 tag; blank = device default
  # volume: 80         # 0–100; blank = full
  # duck: true         # lower TV audio while speaking (default)
  # interrupt: true    # barge in over any current announcement (default); false = queue
```

## 🔊 Play a sound & 🧹 Clear

```yaml
action: tv_assist.play_sound
data:
  target: bedroom_tv
  media_url: "http://…/chime.mp3"   # chime / MP3 / WAV
  # volume: 80

# ---

action: tv_assist.clear
data:
  target: bedroom_tv
  id: "doorbell"            # omit id to clear all
```

## 🕗 On-screen display (dim + clock)

Each TV also exposes `POST http://TV_IP:8455/set/overlay` to control the dimming layer and the
always-on clock remotely (e.g. via a `rest_command`): `dim` 0–95, `clock` true/false, `corner` =
`top_start | top_end | bottom_start | bottom_end`.

## 🧩 Example automation

```yaml
automation:
  - alias: Doorbell to bedroom TV
    trigger:
      - platform: state
        entity_id: binary_sensor.doorbell
        to: "on"
    action:
      - action: tv_assist.notify
        data:
          target: bedroom_tv
          title: "Front door"
          message: "Someone's at the door"
          icon: "mdi:doorbell"
          camera: "camera.front_door"
          duration: 12
```

## 💡 Seeing example values

Every field ships with an example value. To load a fully-populated sample call:

1. **Developer Tools → Actions**, pick **TV Assist: Send notification** (or any action).
2. Switch the editor to **YAML mode** — the **⋮** menu → **Edit in YAML**.
3. Click **FILL EXAMPLE DATA** — Home Assistant drops in every field's example, ready to run.

> [!NOTE]
> The friendly **UI form** does *not* show `example:` values (only `default:` ones like *Duration = 8*),
> so the YAML-mode button above is where the examples appear. The two targeting fields
> (**Device identifier** / **Host**) are intentionally left blank for you to fill with your own TV.

## 🤝 Contributing

Issues and PRs are welcome at [manjotsc/tv-assist-ha](https://github.com/manjotsc/tv-assist-ha/issues).

## 📄 License

Released under the MIT License — see [`LICENSE`](LICENSE).
