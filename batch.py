import fetch_data
import showresults
import subprocess

# List of channels to make forecasts for
channels = ["@Lunduke", "@NaomiBrockwell", "@TheLinuxGamer",
            "@TheCryptoLark", "@CryptoCandor", "@mikenayna",
            "@no1marmadukefan", "@TechFox", "@GaminGHD",
            "@MinutePhysics", "@GamesGlitches",
            "@upside", "@OpenSourceGames", "@paulvanderklay",
            "@JordanBPeterson", "@Crypt0", "@MothersBasement",
            "@imineblocks", "tioaventurabus"]

f = open("forecasts.csv", "w")
f.write("channel_name,forecast_lower,forecast_medium,forecast_upper\n")
f.flush()

for channel in channels:
    data = fetch_data.get_data(channel)
    fetch_data.write_flattened(data)
    subprocess.call(["./main", "-t 10"])
    quantiles = showresults.postprocess()

    f.write(channel + ",")
    f.write(str(quantiles[0]) + ",")
    f.write(str(quantiles[1]) + ",")
    f.write(str(quantiles[2]) + "\n")
    f.flush()

f.close()

