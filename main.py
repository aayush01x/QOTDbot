import json
from datetime import datetime
from datetime import date
import discord
from discord.utils import get
import os
from discord.ext import commands, tasks
import random
from oauth2client.service_account import ServiceAccountCredentials
import gspread
from itertools import cycle
from collections import OrderedDict

intents = discord.Intents.default()
scope = [
    'https://spreadsheets.google.com/feeds',
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive.file',
    'https://www.googleapis.com/auth/drive'
]
creds = ServiceAccountCredentials.from_json_keyfile_name('creds.json', scope)
client2 = gspread.authorize(creds)
client3 = gspread.authorize(creds)
client = commands.Bot(command_prefix="&")
status = cycle(["Hey"])


class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')


@tasks.loop(seconds=10800)
async def change_status():
    await client.change_presence(status=discord.Status.idle,
                                 activity=discord.Game(next(status)))
@client.event
async def on_ready():
    change_status.start()
    print("Bot is ready.")


now_sheet = client2.open("QoTDS GRAM").sheet1
lb_sheet= client3.open("lbforbot").sheet1
#now_sheet.update_cell(6,7,"test")
full_data = now_sheet.get_all_records()
dict_with_points={}
dict_with_chances={}
qotd_solvers=[]
submitted_once=[]
cummulative_points={}
"""
full data : [{Heading1:value1, Heading2:value2},{Heading1:value11, Heading2:value12},{Heading1:value111, Heading2:value222}]

To fetch:
full data[i]              <- gives dictionary position (i+1)
full data[i][Title name]  <-gives key corresponding to it
"""
#list_notdone=[]
#Posting Problem(have to change to specfic channel)
@client.command()
async def post(ctx):
    #getting current problem
    #list_notdone.clear()
    dict_with_chances.clear()
    dict_with_points.clear()
    qotd_solvers.clear()
    submitted_once.clear()
    full_data = now_sheet.get_all_records()
    global list_notdone
    list_notdone=[]
    for starting_noob in range(len(full_data)):
      #print(full_data[starting_noob].get('Posted'))
      if full_data[starting_noob].get('Posted') == "":
        
        list_notdone.append(starting_noob)
        #print(full_data[starting_noob])
        print(list_notdone)
    #print(list_notdone[0])    
    #print(full_data)
    #print(len(full_data))
    #print(full_data[list_notdone[0]])
    
    message = "**QoTD: " + str(full_data[list_notdone[0]]["Sr. No."]) + " **" 
    """
    await ctx.send(message)
    await ctx.send(full_data[list_notdone[0]]["Problem Link"])
    message2 = "**Season: **" +  + "\n" + "**Points: **"+ 
    await ctx.send(message2)
    """
    global embed
    embed = discord.Embed(
        title=message,
        description="Send answer to this problem in dm to me. Just send the answer in one message without anything else.",
        colour=discord.Color.blue()
    )
    
    embed.set_image(url=full_data[list_notdone[0]]["Problem Link"])
    embed.add_field(name="Season", value=str(full_data[list_notdone[0]]["Season"]), inline=True)
    embed.add_field(name="Points", value=str(full_data[list_notdone[0]]["Points"]), inline=True)
    await ctx.send(embed=embed)
    print(starting_noob)
    now_sheet.update_cell(list_notdone[0]+2,5,"Done")
    now_sheet.update_cell(list_notdone[0]+2,9,"Yes")
    


def checkWhole(x):
    try:
        x =str(x)
        for t in x:
          if not t.isnumeric():
            return False
          return True  
        return x >= 0
    except:
        return False

#Getting anwsers
@client.event
async def on_message(message):
    empty_array = []
    modmail_channel = discord.utils.get(client.get_all_channels(), name="mod-mail")
    if message.author == client.user:
        return
    if str(message.channel.type) == "private":
        if message.attachments != empty_array and not message.author.bot:
            pass

        else:
            k = message.author.id
            embed = discord.Embed(title="potd-log",
                                  colour=message.author.colour,
                                  timestamp=datetime.utcnow())

            embed.set_thumbnail(url=message.author.avatar_url)
            fields = [("Member", message.author.display_name, False), ("Message", message.content, False)]
            for name, value, inline in fields:
                embed.add_field(name=name, value=value, inline=inline)
            await modmail_channel.send(embed=embed)


            solver_name=str(message.author.display_name)
            hmm11=str(message.content).replace(" ", "")  
            
#total chances=3
            print(message.content)
            print(full_data[list_notdone[0]]["Answer"])
            if str(message.content)==str(full_data[list_notdone[0]]["Answer"]):
              person=message.author.name+"#"+message.author.discriminator
              if person not in qotd_solvers:
                qotd_solvers.append(person)
                if person not in cummulative_points:
                  cummulative_points[person]=0
                if person not in submitted_once: 
                  #got correct in 1st try
                  
                  dict_with_points[person]=full_data[list_notdone[0]]["Points"]
                  await message.author.send("Congratulations! You got "+str(full_data[list_notdone[0]]["Points"]) + " points for getting the problem correct.")
                  await modmail_channel.send(message.author.mention+ " got **"+str(full_data[list_notdone[0]]["Points"])+"** points for getting QoTD "+str(full_data[list_notdone[0]]["Sr. No." ])+ " correct.")
                  cummulative_points[person]+=float(int(full_data[list_notdone[0]]["Points"]))
                  await modmail_channel.send(cummulative_points)
                if person in submitted_once:
                  if dict_with_chances.get(person)==2:
                    await message.author.send("Congratulations! You got "+str(int(full_data[list_notdone[0]]["Points"])*0.5) + " points for getting the problem correct in second try.")
                    await modmail_channel.send(message.author.mention+ " got **"+str(int(full_data[list_notdone[0]]["Points"])*0.5)+"** points for getting QoTD "+str(full_data[list_notdone[0]]["Sr. No." ])+ " correct.")
                    dict_with_points[person]=full_data[list_notdone[0]]["Points"]*(0.5)
                    cummulative_points[person]+=float((int(full_data[list_notdone[0]]["Points"]))*0.5)
                    await modmail_channel.send(cummulative_points)
                  if dict_with_chances.get(person)==1:
                    await message.author.send("Congratulations! You got "+str(int(full_data[list_notdone[0]]["Points"])*0.25) + " points for getting the problem correct in third try.")
                    await modmail_channel.send(message.author.mention+ " got **"+str(int(full_data[list_notdone[0]]["Points"])*0.25)+"** points for getting QoTD "+str(full_data[list_notdone[0]]["Sr. No." ])+ " correct.")
                    dict_with_points[person]=full_data[list_notdone[0]]["Points"]*(0.25)
                    cummulative_points[person]+=float((int(full_data[list_notdone[0]]["Points"]))*0.25)
                    await modmail_channel.send(cummulative_points)
                  if dict_with_chances.get(person)==0:
                    await message.author.send("Sorry, You used up all your chances.")
    
              await modmail_channel.send("**"+person + "** got it correct.")
                
            if str(message.content)!=str(full_data[list_notdone[0]]["Answer"]) and checkWhole(message.content)==True:
              
              await message.author.send("Thats incorrect.")
              person=message.author.name+"#"+message.author.discriminator
              if person not in submitted_once and person not in qotd_solvers:
                submitted_once.append(person)
                dict_with_chances[person]=2
                await message.author.send("You have **2** more chances left.")

              elif person in submitted_once and dict_with_chances.get(person)==2 and person not in qotd_solvers:
                dict_with_chances[person]=1
                await message.author.send("You have **1** more chance left.")
              elif person in submitted_once and dict_with_chances.get(person)==1 and person not in qotd_solvers:
                dict_with_chances[person]=0
                await message.author.send("You have no more chances left.")
                await modmail_channel.send(person+ " used up all chances.")
                cummulative_points.get(person)
                dict_with_points[person]=0
              elif person in submitted_once and dict_with_chances[person]==0:
                await message.author.send("Sorry, You used up all your chances.")
                if person not in cummulative_points:
                  cummulative_points[person]=0
                await modmail_channel.send(cummulative_points)                  
                

              

            if str(message.content)!=str(full_data[list_notdone[0]]["Answer"]) and checkWhole(message.content)==False:
              await message.author.send("Please enter your answer as a whole number.") 
    await client.process_commands(message)

@client.command()
async def postcommlb(ctx):#official
  one_more_random_dictionary=[]
  a_dictionary =  {k: v for k, v in sorted(cummulative_points.items(), key=lambda item: item[1])}
  d_dictionary = dict(reversed(list(a_dictionary.items())))


  for sss in d_dictionary:
      listing_for_something=[]
      for rite in str(sss):
          listing_for_something.append(rite)
      length=len(listing_for_something)
      space_length = 40
      remaining_length = space_length - length
          
      line = sss+ " "*remaining_length+str(d_dictionary.get(sss))
      one_more_random_dictionary.append(line)
  cummulative_lb_message= "\n".join(one_more_random_dictionary)

  modmail_channel = discord.utils.get(client.get_all_channels(), name="mod-mail")
  await modmail_channel.send("**"+"Season "+str(full_data[list_notdone[0]]["Season"])+ " Leaderboard** \n"+ "```"+cummulative_lb_message+"```")
@client.command()
async def showcommlb(ctx):#formods
  one_more_random_dictionary=[]
  a_dictionary =  {k: v for k, v in sorted(cummulative_points.items(), key=lambda item: item[1])}
  d_dictionary = dict(reversed(list(a_dictionary.items())))


  for sss in d_dictionary:
      listing_for_something=[]
      for rite in str(sss):
          listing_for_something.append(rite)
      length=len(listing_for_something)
      space_length = 40
      remaining_length = space_length - length
          
      line = sss+ " "*remaining_length+str(d_dictionary.get(sss))
      one_more_random_dictionary.append(line)
  cummulative_lb_message= "\n".join(one_more_random_dictionary)

  modmail_channel = discord.utils.get(client.get_all_channels(), name="mod-mail")
  await modmail_channel.send("**"+"Season "+str(full_data[list_notdone[0]]["Season"])+ " Leaderboard** \n"+ "```"+cummulative_lb_message+"```")
@client.command()
async def clearcommlb(ctx):
  cummulative_points.clear()
  await ctx.send("Cleared cummulative leaderboard.")
@client.command()
async def postlb(ctx):#official
  one_more_random_dictionary2=[]
  a_dictionary2 =  {k: v for k, v in sorted(dict_with_points.items(), key=lambda item: item[1])}
  d_dictionary2 = dict(reversed(list(a_dictionary2.items())))


  for ssss in d_dictionary2:
      listing_for_something2=[]
      for riter in str(ssss):
          listing_for_something2.append(riter)
      length=len(listing_for_something2)
      space_length1 = 40
      remaining_length1 = space_length1 - length
          
      line = ssss+ " "*remaining_length1+str(d_dictionary2.get(ssss))
      one_more_random_dictionary2.append(line)
  cummulative_lb_message1= "\n".join(one_more_random_dictionary2)  
  modmail_channel = discord.utils.get(client.get_all_channels(), name="mod-mail")
  await modmail_channel.send("**"+"QoTD "+str(full_data[list_notdone[0]]["Sr. No."])+ " Leaderboard** \n"+ "```"+cummulative_lb_message1+"```")
@client.command()
async def showlb(ctx):#formods
  one_more_random_dictionary2=[]
  a_dictionary2 =  {k: v for k, v in sorted(dict_with_points.items(), key=lambda item: item[1])}
  d_dictionary2 = dict(reversed(list(a_dictionary2.items())))


  for ssss in d_dictionary2:
      listing_for_something2=[]
      for riter in str(ssss):
          listing_for_something2.append(riter)
      length=len(listing_for_something2)
      space_length1 = 40
      remaining_length1 = space_length1 - length
          
      line = ssss+ " "*remaining_length1+str(d_dictionary2.get(ssss))
      one_more_random_dictionary2.append(line)
  cummulative_lb_message1= "\n".join(one_more_random_dictionary2)  
  modmail_channel = discord.utils.get(client.get_all_channels(), name="mod-mail")
  await modmail_channel.send("**"+"QoTD "+str(full_data[list_notdone[0]]["Sr. No."])+ " Leaderboard** \n"+ "```"+cummulative_lb_message1+"```")  
@client.command()
async def echo(ctx, *,message):
  if ctx.message.author=="856563716865916928":#add of qotd creators
    modmail_channel = discord.utils.get(client.get_all_channels(), name="mod-mail")
    await(modmail_channel.send(str(message)))
  if ctx.message.author!="856563716865916928":#add_of qotd creators
    await ctx.send("Sorry! "+ctx.message.author.mention+" You don't have permissions to use this command." ) 


client.run('')

#channels to change: got correct(ping), post, postcommlb, postsoln maybe, add pings,echo