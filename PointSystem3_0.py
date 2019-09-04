import tkinter as tk
from bs4 import BeautifulSoup
import requests
import math
import xlsxwriter

modi = ['bw', 'rush', 'sg', 'tsg', 'gd', 'jd', 'mb', 'pg', 'revo', 'sw', 'tw', 'bb', 'tj', 'ct']


def LastPlaces():

	file = open("LastPlaces.txt","r")
	contents = file.read()

	if len(str(contents)) == 0:
		oldlastplaces = len(modi) * [0]

		firsttime = 1

	else:
		oldlastplaces = contents[1:-1].split(',')

	print('Getting Last Places...')

	LastPlaces = len(modi) * [0]

	for mode in modi:
		print('Getting Lastplace from ' + mode)
	
		lower = int(oldlastplaces[modi.index(mode)])
		if firsttime == 1:
			upper = 100000
		else:
			upper = lower + 50
	
		upper = tryagain(lower, upper, mode)

		while lower != upper:

	
			link = 'https://api-stats.rewinside.tv/leaderboards/' + mode + '?skip=' + str((lower + upper)//2 * 20)
			source = requests.get(link).text
			soup = BeautifulSoup(source, 'lxml')
	
			if len(soup) == 0:
				upper = (lower + upper)//2
			else:
				lower = (lower + upper)//2 + 1

			print(str(lower) + ' : ' + str(upper))
	
		LastPlaces[modi.index(mode)] = lower
		print(LastPlaces)



	file = open("LastPlaces.txt","w")
	file.write(str(LastPlaces))
	file.close()


def tryagain(lower, upper, mode):


	link = 'https://api-stats.rewinside.tv/leaderboards/' + mode + '?skip=' + str(upper*20)

	source = requests.get(link).text
	soup = BeautifulSoup(source, 'lxml')

	
	if len(soup) == 1:
		upper += 100
		print(str(lower) + ' - ' + str(upper))
		upper = tryagain(lower, upper, mode)
		return(upper)
	else:
		return(upper)


def SinglePlayer():

	
	name = Entry.get()

	Data = GetStats(name, 1)

	score = Data[1]
	bestrank = Data[2]
	
	print(20 * '-')		
	print('Score: ' + str(score))
	print('Bestrank: ' + str(bestrank))
	print(20 * '-')	

def GetStats(name, single):

	file = open("LastPlaces.txt","r")
	contents = file.read()
	LastPlaces = contents[1:-1].split(',')

	for i in range(len(LastPlaces)):
		LastPlaces[i] = int(LastPlaces[i]) * 20



	link = 'https://api-stats.rewinside.tv/players/' + str(name) + '/stats'
	source = requests.get(link).text
	soup = BeautifulSoup(source, 'lxml')
	statsdata = str(soup)[16:-19]
	statsdata = statsdata.split(',')

	i = -1
	mode = 0
	score = 0

	bestrank = 1000000000

	while i != len(statsdata)-1:
		i += 1
		if statsdata[i][1:1+len(modi[mode])] == modi[mode]:
			if len(statsdata[i][11+len(modi[mode]):]) == 0:
				rank = LastPlaces[mode]
			else:
				rank = int(statsdata[i][11+len(modi[mode]):])

			if rank < bestrank:
				bestrank = rank

			if rank == 0:
				rank = LastPlaces[mode]

			points = math.log(LastPlaces[mode]/rank, 2)

			score += points

			if single == 1:
				print(modi[mode] + ': ' + str(round(points,2)))
			mode += 1

		if mode == len(modi):
			break

	return [name, score, bestrank]

def sorting(Names2, Scores2, Bestranks2):

	sortedpoints = []
	sortednames = []
	sortedbestranks = []

	for i in range(len(Scores2)):
		highest = 0
		for element in range(len(Scores2)): #chooses the highest element
			if highest < Scores2[element]:
				highest = Scores2[element]
				best = element
		sortedpoints.append(highest) #adds the playerdata of the best player to the new lists
		sortednames.append(Names2[best])
		sortedbestranks.append(Bestranks2[best])

		Scores2[best] = 0


	return [sortednames, sortedpoints, sortedbestranks]


def double(Names, Scores, Bestranks): #removes all doubles

	i = 0
	while i < len(Scores) - 1:
		namechecked = Names[i] #sets the name currently getting checked
		if namechecked == Names[i+1]: #if the name is double, then remove the name (plus its data) once
			Names.pop(i)
			Scores.pop(i)
			Bestranks.pop(i)
		else:
			i += 1

	return [Names, Scores, Bestranks]


def excel(Names, Scores, Bestranks, auto): #adds the data to an excel-spreadsheet called 'PointSystem'


	if auto == 1:
		workbook = xlsxwriter.Workbook('PointSystemAuto.xlsx') #makes 2 different documents depending on if auto is on or not
	else:
		workbook = xlsxwriter.Workbook('PointSystemManual.xlsx')
	worksheet = workbook.add_worksheet()

	bold = workbook.add_format()
	bold.set_bold()

	worksheet.write(0, 0, 'Rang', bold) #writes the titles in bold
	worksheet.write(0, 1, 'Name', bold)
	worksheet.write(0, 2, 'Punkte', bold)
	worksheet.write(0, 3, 'Bester Rang', bold)

	for row in range(0,len(Names)): #writes the data
		worksheet.write(row + 1,0,row + 1)
		worksheet.write(row + 1,1,Names[row])
		worksheet.write(row + 1,2,Scores[row])
		worksheet.write(row + 1,3,Bestranks[row])

	workbook.close()
	print('done')



def Auto():

	Names = ExtraNames()

	maxpages = 50

	for mode in modi:

		for page in range(maxpages):

			print(str(mode) + ': ' + 'Page ' + str(page) + ' of ' + str(maxpages))

			link = 'https://api-stats.rewinside.tv/leaderboards/' + str(mode) + '?skip=' + str(page * 20)
			source = requests.get(link).text
			soup = BeautifulSoup(source, 'lxml')

			statsdata = str(soup)[16:-19]
			statsdata = statsdata.split(',')

			for i in range(len(statsdata)):
				if statsdata[i][1:7] == 'player':
					name = statsdata[i][10:-1]
					Names.append(name)

	Scores = []
	Bestranks = []

	counter = 1

	for name in Names:

		counter += 1

		if counter % 10 == 0:
			print('Progress: ' + str(round(100*counter/len(Names),1)) + '%')

		Data = GetStats(name, 0)
		score = Data[1]
		bestrank = Data[2]

		Scores.append(score)
		Bestranks.append(bestrank)


	Data = sorting(Names, Scores, Bestranks)

	Data = double(Data[0], Data[1], Data[2])

	Names = Data[0]
	Scores = Data[1]
	Bestranks = Data[2]

	for i in range(len(Scores)):
		Scores[i] = round(Scores[i], 2)

	excel(Names, Scores, Bestranks, 1)

def ExtraNames():
	file = open("Names.txt","r")
	contents = file.read()

	if len(str(contents)) == 0:
		Names = []

	else:
		Names2 = contents[1:-1].split(',')

		Names = []

		for name in Names2:
			if name[0] == ' ':
				Names.append(name[1:])
			else:
				Names.append(name)

	return Names

def Manual():

	Names = ExtraNames()
	Scores = []
	Bestranks = []

	counter = 1

	for name in Names:

		counter += 1

		if counter % 10 == 0:
			print('Progress: ' + str(round(100*counter/len(Names),1)) + '%')

		Data = GetStats(name, 0)
		score = Data[1]
		bestrank = Data[2]

		Scores.append(score)
		Bestranks.append(bestrank)


	Data = sorting(Names, Scores, Bestranks)

	Data = double(Data[0], Data[1], Data[2])

	Names = Data[0]
	Scores = Data[1]
	Bestranks = Data[2]


	for i in range(len(Scores)):
		Scores[i] = round(Scores[i], 2)

	excel(Names, Scores, Bestranks, 0)



root = tk.Tk()

root.title('Point System')

normalfont = ("Helvetica", 18)
bigfont = ("Helvetica", 24, "bold")

tk.Button(root, font=bigfont, text='Auto', command=Auto).grid(row=0, column=0, sticky='nesw')
tk.Button(root, font=bigfont, text='Manual', command=Manual).grid(row=0, column=1, sticky='nesw')

tk.Button(root, font=normalfont, text='Get Playerstats', command=SinglePlayer).grid(row=1, column=1, sticky='nesw')
Entry = tk.Entry(root, font=normalfont)
Entry.grid(row=1, column=0, sticky='nesw')
tk.Button(root, font=normalfont, text='Update Lastnames', command=LastPlaces).grid(row=2, column=0, columnspan=2, sticky='nesw')

root.mainloop()
