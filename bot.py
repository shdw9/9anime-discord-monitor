from bs4 import BeautifulSoup
from colorthief import ColorThief
import discord, asyncio, requests, os

logsFile = "logs.txt"

discordChannelId = ""

###

bot = discord.Bot(intents=discord.Intents.all())

def rgb_to_hex(r,g,b):
    return int('0x%02x%02x%02x' % (r,g,b),0)

async def getDominantColor(imageUrl):
    r = requests.get(imageUrl)

    f = open("thumbnail.jpg","wb")
    f.write(r.content)
    f.close()

    color_thief = ColorThief('thumbnail.jpg')
    dominant_color = color_thief.get_color(quality=1)

    os.remove("thumbnail.jpg")

    return rgb_to_hex(dominant_color[0],dominant_color[1],dominant_color[2])

async def scrape():
    print("Looking for new anime releases ...")

    # read logsFile, to notify anime or not
    with open(logsFile,"r",encoding="utf-8") as f:
        logs = f.read()

    r = requests.get("https://9anime.to/filter?keyword=&country%5B%5D=120822&sort=recently_updated&vrf=")
    soup = BeautifulSoup(r.text,"html.parser")
    items = soup.find_all("div",class_="inner")
    for item in items:
        if "ani poster tip" in str(item):
            title = item.find("a",class_="name d-title").text.strip()
            genre = item.find("div",class_="genre").text.strip()
            episode = item.find("span",class_="ep-status sub").text.strip()
            thumbnail = item.find("img")["src"]
            link = "https://9anime.to" + item.find("a")["href"] + "/ep-" + episode

            # check if anime/episode has already been notified
            if title + " " + episode not in logs:

                dominantColor = await getDominantColor(thumbnail)

                # send discord embed
                embed = discord.Embed(title=title,url=link,description="**Episode** " + episode,color=dominantColor)
                embed.add_field(name="Genres",value = genre) if len(genre.split(",")) > 0 else embed.add_field(name="Genre",value = genre)
                embed.set_image(url=thumbnail)
                await bot.get_channel(int(discordChannelId)).send(embed=embed)

                # write to log
                with open (logsFile,"a",encoding="utf-8") as f:
                    f.write(title + " " + episode + "\n")
                
                print(title + " " + episode)

async def background_task():
        await bot.wait_until_ready()
        while True:
            try:
                await scrape()
                await asyncio.sleep(120)
            except Exception as e:
                print(e)
                pass

bot.loop.create_task(background_task())

bot.run("")
