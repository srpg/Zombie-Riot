import path
from messages import SayText2
from translations.strings import LangStrings

__FILEPATH__    = path.Path(__file__).dirname()
chat = LangStrings(__FILEPATH__ + '/messages/chat')

#===================
# Chat Messages
#===================

Game    = SayText2(chat['Game'])
Market  = SayText2(chat['Market'])
Won     = SayText2(chat['Win'])
New     = SayText2(chat['Restart'])
Weapon  = SayText2(chat['Buy'])
welcome = SayText2(chat['Welcome_info'])
Potion  = SayText2(chat['Potion'])
Rebuy   = SayText2(chat['Rebuy'])
Alive   = SayText2(chat['Alive'])
