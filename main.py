# -*- coding: utf-8 -*-

'''
This programm creates xml-feed of recipes for yandex-snippets
like this:
http://help.yandex.ru/webmaster/realEntitiesExample.xml
'''
from urllib.request import urlopen
from lxml import etree
from lxml.html import fromstring

URL = "http://valzevul.ru/map/" #list of all entries
IMG_URL = "http://valzevul.ru/wp-content/uploads/" #pre-url for food images
PATTERN = "рецепт" #pattern for recipes
TIME = "Время приготовления" #pattern for time
INGREDIENTS = "Ингредиенты" #pattern for ingredients
STOP_ARRAY = ["Ваши рецепты", "061", "126"] #list of non-recipes links with recipes pattern
FILE = "recipes.xml" #name of output file

def add_to_xml(name, url, typeId, time, ingredients, instruction, imgs):
	'''
	@name: name of recipe
	@url: url to recipe
	@typeId: type of food (more about format here:
			http://help.yandex.ru/webmaster/?id=1111973#1112008)
	@time: time of cooking
	@ingredients: list of ingredients
	@instruction: list of instructions
	@imgs: list of links to images
	'''
	recipe = etree.SubElement(root, "recipe")
	tmp = etree.SubElement(recipe, "name")
	tmp.text = name
	tmp = etree.SubElement(recipe, "url")
	tmp.text = url
	tmp = etree.SubElement(recipe, "type")
	tmp.text = typeId
	count = 0
	for i in ingredients:
		ingredient = etree.SubElement(recipe, "ingredient")
		tmp = etree.SubElement(ingredient, "name")
		tmp.text = i
	for i in instruction:
		if (INGREDIENTS in i) or (TIME in i):
			continue
		else:
			tmp = etree.SubElement(recipe, "instruction")
			tmp.text = i
	for i in imgs:
		tmp = etree.SubElement(recipe, "photo")
		tmp.text = imgs[count]
	tmp = etree.SubElement(recipe, "final-photo")
	tmp.text = imgs[-1]
def parse_recipe(name, link, data):
	'''
	@name: name of recipe
	@link: link to recipe
	@data: etree.HtmlElement with recipe
	'''
	recipeTime = 0
	recipeIngredients = []
	recipeSteps = []
	imgSteps = []
	print(name)
	for item in data.iter(tag = "p"):
		if item.text:
			if (TIME in item.text):
				recipeTime = item.text
			recipeSteps.append(item.text)
	for item in data.iter(tag = "img"):
		if item.get("src") and (IMG_URL in item.get("src")):
			imgSteps.append(item.get("src"))
	for item in data.iter(tag = "ul"):
		#if item.getprevious().text and (INGREDIENTS in item.getprevious().text):
		if (item.getprevious() is not None) and (INGREDIENTS in item.getprevious().text):
			for product in item.iterchildren():
				if product.text:
					recipeIngredients.append(product.text)
	add_to_xml(name, link, typeId, recipeTime, recipeIngredients, recipeSteps, imgSteps)
def parse_page(name, link):
	'''
	@name: name of recipe
	@link: link to recipe
	'''
	html = urlopen(link).read().decode('utf8');
	page = fromstring(html) 
	page.make_links_absolute(URL)
	for item in page.iter(tag = "div"):
		if item.get("class") == "entry":
			parse_recipe(name, link, item)
			break
def create_page(page):
	'''
	@page: page with all links
	'''
	for link in page.iterlinks():
		flag = False
		for el in link[0].iter():
			if el.text and (PATTERN in el.text):
				for i in STOP_ARRAY:
					if i in el.text:
						flag = True
				if flag:
					break
				arrayOfLinks[el.text] = link[2]
	for item in arrayOfLinks.items():
		parse_page(item[0], item[1])

def main():
	root = etree.Element("entities")
	typeId = "Еда"
	arrayOfLinks = {}
	html = urlopen(URL).read().decode('utf8');
	page = fromstring(html) 
	page.make_links_absolute(URL)
	create_page(page)
	with open(FILE, 'w') as f:
		f.write(etree.tostring(root, pretty_print = True, encoding = "unicode"))
		f.close()
	return 0

if __name__ == '__main__':
	main()
