import pandas as pd 
import Tkinter

ag1_0=pd.read_csv("recJob2/gameAllroundsP1_try_4_game_0.csv");
ag2_0=pd.read_csv("recJob2/gameAllroundsP2_try_4_game_0.csv");
ag3_0=pd.read_csv("recJob2/gameAllroundsP3_try_4_game_0.csv");
ag4_0=pd.read_csv("recJob2/gameAllroundsP4_try_4_game_0.csv");
ag1_1=pd.read_csv("recJob2/gameAllroundsP1_try_4_game_1.csv");
ag2_1=pd.read_csv("recJob2/gameAllroundsP2_try_4_game_1.csv");
ag3_1=pd.read_csv("recJob2/gameAllroundsP3_try_4_game_1.csv");
ag4_1=pd.read_csv("recJob2/gameAllroundsP4_try_4_game_1.csv");


ag1_0=ag1_0.drop(['round', 'uuid'], axis=1)

print(ag1_0.plot())
