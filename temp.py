import requests
import json
import os
import discord
from discord.ext import tasks, commands
from discord import FFmpegPCMAudio
from discord import Member
from discord.ext.commands import has_permissions, MissingPermissions
from twitchAPI.twitch import Twitch
from discord.utils import get

from apikeys import * # imports variables from local apikeys.py




