# SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
#
# SPDX-License-Identifier: Unlicense
import time
from adafruit_magtag.magtag import MagTag
from adafruit_datetime import datetime
magtag = MagTag()

magtag.add_text(
    text_position=(5, 0), text_scale=1, text_anchor_point=(0, 0), line_spacing=1
)

while True:
    magtag.get_local_time("America/Chicago")
    text = "Checked at {}\n".format(datetime.now())
    magtag.get_local_time("Etc/UTC")

    acurite = magtag.get_io_group("acurite").get("feeds")
    acuritewarn = magtag.get_io_group("acurite-warn").get("feeds")
    acuritecrit = magtag.get_io_group("acurite-crit").get("feeds")

    warn_active = False
    crit_active = False

    for feed in acurite:
        timedelta = datetime.now() - datetime.fromisoformat(feed.get("updated_at").replace("Z",""))
        feed_name = feed.get("name")
        current_temp = float(feed.get("last_value"))
        warn_temp = float([d['last_value'] for d in acuritewarn if d['name'] == feed_name][0])
        crit_temp = float([d['last_value'] for d in acuritecrit if d['name'] == feed_name][0])

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
    elif warn_active:
        print("Warning alert active!")
    else:
        print("No alerts.")

    time.sleep(60)
    #magtag.exit_and_deep_sleep(10)