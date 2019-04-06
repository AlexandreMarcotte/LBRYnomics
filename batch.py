import fetch_data
import numpy as np
import showresults
import subprocess

# List of channels to make forecasts for
channels = ["@Lunduke", "@NaomiBrockwell", "@TheLinuxGamer",
            "@TheCryptoLark", "@CryptoCandor", "@mikenayna",
            "@no1marmadukefan", "@TechFox", "@GaminGHD",
            "@MinutePhysics", "@GamesGlitches",
            "@upside", "@OpenSourceGames", "@paulvanderklay",
            "@JordanBPeterson", "@Crypt0", "@MothersBasement",
            "@imineblocks", "@tioaventurabus", "@leckakay", "@Luke",
            "@akirathedon", "@davidpakman"]

f = open("forecasts.csv", "w")
f.write("channel_name,forecast_low,forecast_medium,forecast_high\n")
f.flush()

for channel in channels:
    data = fetch_data.get_data(channel)
    fetch_data.write_flattened(data)
    subprocess.call(["./main", "-t 10"])
    quantiles = showresults.postprocess()

    f.write(channel + ",")
    f.write(str(np.round(quantiles[0], 2)) + ",")
    f.write(str(np.round(quantiles[1], 2)) + ",")
    f.write(str(np.round(quantiles[2], 2)) + "\n")
    f.flush()

f.close()

