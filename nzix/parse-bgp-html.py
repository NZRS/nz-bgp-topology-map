import bs4

with open('rs1.wix.nzix.net.html') as f:
    soup = bs4.BeautifulSoup(f)

for p in soup.find_all('pre'):
    print p.get_text()
