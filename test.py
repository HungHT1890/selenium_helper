from HungHT1890 import HungHT1890Sele

def test_selenium():
    url = 'https://facebook.com'
    support = HungHT1890Sele(chrome_path='chromedriver.exe',app_url=url)
    driver = support.chrome_setup()
    support.open_url(driver,url='https://google.com',js=True)
    
    
    input("Enter to close")
    driver.quit()



if __name__ == '__main__':
    # test chrome
    test_selenium()
    