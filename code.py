# SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
#
# SPDX-License-Identifier: Unlicense
import time
from adafruit_magtag.magtag import MagTag
from adafruit_datetime import datetime
magtag = MagTag()

if magtag.peripherals.battery < 3.5:
    print("Battery low. Sleeping for 1 hour.")
    magtag.add_text(text_position=(50, (magtag.graphics.display.height // 2) - 1,), text_scale=3,)
    magtag.set_text("Low Battery!")
    magtag.peripherals.neopixels.fill((0,0,0))
    magtag.peripherals.speaker_disable = True
    magtag.peripherals.neopixel_disable = True
    magtag.exit_and_deep_sleep(3600)

magtag.add_text(
    text_position=(5, 0), text_scale=1, text_anchor_point=(0, 0), line_spacing=1
)

while True:
    magtag.get_local_time("America/Chicago")
    text = "Checked at {}   Batt: {:.2f}V\n".format(datetime.now(), magtag.peripherals.battery)
    magtag.get_local_time("Etc/UTC")

    magtag.push_to_io("magtag.battery", magtag.peripherals.battery)
    magtag.push_to_io("magtag.light", magtag.peripherals.light)
    
    acurite = magtag.get_io_group("acurite").get("feeds")
    acuritewarn = magtag.get_io_group("acurite-warn").get("feeds")
    acuritecrit = magtag.get_io_group("acurite-crit").get("feeds")

    warn_active = False
    crit_active = False

    for feed in acurite:
        timedelta = datetime.now() - datetime.fromisoformat(feed.get("updated_at").replace("Z",""))
        feed_name = feed.get("name")
        feed_key = feed.get("key").split(".")[1]
        current_temp = float(feed.get("last_value"))
        warn_temp = float([d['last_value'] for d in acuritewarn if d['key'] == "acurite-warn." + feed_key][0])
        crit_temp = float([d['last_value'] for d in acuritecrit if d['key'] == "acurite-crit." + feed_key][0])

        status = '        '
        if current_temp > crit_temp:
            status = "CRITICAL"
            crit_active = True
        elif current_temp > warn_temp:
            status = "WARNING "
            warn_active = True
        print("{:<15} {:6.2f} {} {} {} - {:.0f} min ago".format(feed_name, current_temp, warn_temp, crit_temp, status, timedelta.total_seconds() / 60))
        text += "{:<15} {:6.2f} {} - {:.0f} min ago\n".format(feed_name, current_temp, status, timedelta.total_seconds() / 60)

    magtag.set_text(text)
    if crit_active:
        print("Critical alarm active!")
        for i in range(10):
            magtag.peripherals.neopixels.fill((255,0,0))
            magtag.peripherals.play_tone(1568, 0.50)
    elif warn_active:
        print("Warning alert active!")
        for i in range(3):
            magtag.peripherals.neopixels.fill((255,255,0))
            magtag.peripherals.play_tone(1318, 0.10)
    else:
        print("No alerts.")
    
    magtag.peripherals.neopixels.fill((0,0,0))
    magtag.peripherals.speaker_disable = True
    magtag.peripherals.neopixel_disable = True
    
    #time.sleep(60)
    magtag.exit_and_deep_sleep(300)

