import fetch_data
import numpy as np
import showresults
import subprocess

# List of channels to make forecasts for
channels = sorted(["@Lunduke", "@NaomiBrockwell", "@TheLinuxGamer",
                   "@TheCryptoLark", "@CryptoCandor", "@mikenayna",
                   "@no1marmadukefan", "@TechFox", "@GaminGHD",
                   "@MinutePhysics", "@GamesGlitches",
                   "@upside", "@OpenSourceGames", "@paulvanderklay",
                   "@JordanBPeterson", "@Crypt0", "@MothersBasement",
                   "@imineblocks", "@tioaventurabus", "@leckakay", "@Luke",
                   "@akirathedon", "@davidpakman", "@timcast", "@AntiMedia",
                   "@water", "@bitcoinandfriends", "@ShutupAndPlay",
                   "@reenthused", "@CatholicHomilies", "@NameThatTune",
                   "@txgarage", "@TipWhatYouLike", "@MusicPlanet",
                   "@3Blue1Brown", "@altcoinbuzz", "@BrendonBrewer",
                   "@anton", "@ModerateConservative", "@LBRY-Social",
                   "@zO-Music", "@KhanAcademy", "@Michaelcraigheadart",
                   "@postjazzrdg", "@kcSebOfficial",
                   "@DanielSibisan", "@jeradhill", "@JuliaGalef",
                   "@NorVegan", "@VeganGains",
                   "@KJamesElliott#36aab723dc34a5e5d4173436f01c7c3457493201",
                   "@veritasium", "@radiodrama"],
                    key=lambda s: s.lower())

f = open("forecasts.csv", "w")
f.write("channel_name,months_active,total_tips_received,forecast_low,forecast_medium,forecast_high,notes\n")
f.flush()

for channel in channels:
    data = fetch_data.get_data(channel)
    fetch_data.write_flattened(data)

    import yaml
    yaml_file = open("data.yaml")
    data = yaml.load(yaml_file, Loader=yaml.SafeLoader)
    yaml_file.close()

    subprocess.call(["./main", "-t 10"])
    quantiles = showresults.postprocess()

    f.write(channel + ",")
    f.write(str(np.round((data["t_end"] - data["t_start"])/17532.0, 2)) + ",")
    f.write(str(np.round(np.sum(data["amounts"]), 2)) + ",")
    f.write(str(np.round(quantiles[0], 2)) + ",")
    f.write(str(np.round(quantiles[1], 2)) + ",")
    f.write(str(np.round(quantiles[2], 2)) + ",")

    if data["t_end"] - data["t_start"] < 17532.0:
        f.write("channel has existed for less than one month")
    f.write("\n")
    f.flush()

f.close()

