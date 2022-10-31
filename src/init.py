import os
import julia

julia.install(julia='\\'.join(os.path.dirname(os.path.abspath(__file__)).split('\\')[:-1]) + '\\runtime\\bin\\julia.exe')