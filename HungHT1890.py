from time import sleep
from traceback import print_exc
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait as WebWait
from selenium.webdriver.common.action_chains import ActionChains as ActChain
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.common.by import By
from os import path , makedirs
from subprocess import check_output , CREATE_NO_WINDOW
from zipfile import ZipFile


def create_foler(folder_name):
    if not path.exists(folder_name):
        makedirs(folder_name)
    return folder_name


class HungHT1890Sele:
    def __init__(self,
                chrome_path = 'chromedriver.exe',
                use_proxy = False,
                proxy = False,
                extension = '',
                useragent = '',
                app_url = '',
                window_size = (500,800),
                image = True,
                incognito = False
                 ):
        self.chrome_path = chrome_path
        self.use_proxy = use_proxy
        self.proxy = proxy
        self.extension = extension
        self.useragent = useragent
        self.app_url = app_url
        self.window_size = window_size
        self.image = image
        self.incognito = incognito
    def proxy_auth(proxy_extracted,file_name='proxy_auth.zip'):
        host , port , user , pwd = proxy_extracted
        manifest_json = """
        {
            "version": "1.0.0",
            "manifest_version": 2,
            "name": "t.me/hunght1890",
            "permissions": ["proxy","tabs","unlimitedStorage","storage","<all_urls>","webRequest","webRequestBlocking"],
            "background": {"scripts": ["background.js"]},
            "minimum_chrome_version":"22.0.0"}"""
        background_js = """
        var config = {mode: "fixed_servers",rules: {singleProxy: {scheme: "http",host: "%s",port: parseInt(%s)},bypassList: ["localhost"]}};
        chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});
        function callbackFn(details){return {authCredentials: {username: "%s",password: "%s"}};}
        chrome.webRequest.onAuthRequired.addListener(callbackFn,{urls: ["<all_urls>"]},['blocking']);
        """ % (host, port, user, pwd)
        with ZipFile(file_name, 'w') as zp:
            zp.writestr("manifest.json", manifest_json)
            zp.writestr("background.js", background_js)
        return file_name

    def chrome_setup(self):
        prefs = {}
        _services = Service(self.chrome_path)
        options = Options()

        # proxy extract
        if self.use_proxy:
            extract = self.proxy.strip()
            length = len(extract)
            if length < 2 or length > 4:
                return False
            if length == 2:
                options.add_argument(f'--proxy-server={self.proxy}')
            
            if length == 4:
                proxy_etension = self.proxy_auth(extract)
                options.add_extension(proxy_etension)
        
        if self.useragent != '':
            options.add_argument(f'--user-agent={self.useragent}')
        
        if self.app_url != '':
            options.add_argument(f'--app={self.app_url}')
        
        if self.extension != '':
            options.add_extension(self.extension)
        
        width , heinght = self.window_size
        
        options.add_argument(f'--window-size={width},{heinght}')
        
        if self.incognito:
            options.add_argument("--incognito")
            
        
        if self.image == False:
            # disable image
            prefs.update({"profile.managed_default_content_settings.images": 2})
        
        # download
        download = create_foler('Download')
        prefs.update({"download.default_directory" : download})
        
        # notification
        prefs.update({"profile.default_content_setting_values.notifications" : 2})
        
        # password
        prefs.update({"credentials_enable_service": False,
                    "profile.password_manager_enabled": False}
                     )
        options.add_experimental_option("prefs",prefs)
        options.add_experimental_option("excludeSwitches",["enable-automation","enable-logging"])
        
        list_option = [
            '--no-sandbox',
            '--ignore-certificate-errors-spki-list',
            '--ignore-ssl-errors',
            '--disable-gpu',
            '--disable-infobars',
            '--start-maximized',
            '--disable-logging',
            '--ignore-certificate-errors',
            '--allow-insecure-localhost'
        ]
        for _option in list_option:
            options.add_argument(_option)
        
        try:
            driver = Chrome(service=_services,options=options)
            return driver
        except Exception as exp:
            with open('driver.log','w',encoding='utf-8') as f:
                print_exc(file=f)
                
            return False
    
    def run_js(self,driver,js_code):
        return driver.execute_script(js_code)
    
    "Mở url"
    def open_url(self,driver,url,js=False,switch=False,max_get_tab=30):
        if js:
            driver.execute_script(f"window.open('{url}')")
            # chyem qua tab vua mo bang js
            if switch:
                windows = driver.window_handles
                for x in range(max_get_tab):
                    
                    windows = driver.window_handles
                    if len(windows) >= 2:
                        driver.switch_to.window(windows[1])
                        return True
                    sleep(1)
                    print(f'Wait {max_get_tab} seconds for switch tab',end='\r')
                
                if len(windows) < 2:
                    return False
        else:
            driver.get(url)
            
    "Đóng tab hoặc toàn bộ driver"
    def close_driver(self,driver,tab_index=0,max_get_tab = 30):
        windows = []
        close_status = True
        if tab_index != 0:
            windows = []
            for x in range(max_get_tab,0,-1):
                windows = driver.window_handles
                if len(windows) >= (tab_index + 1) :
                    driver.switch_to.window(windows[tab_index])
                    driver.close()
                    driver.switch_to.window(windows[0])
                    break
                print(f'Wait {x-1} seconds for close tab {tab_index}',end='\r')
                sleep(1)
                
            if len(windows) < (tab_index + 1):
                print(f'\nNo Exist Tab {tab_index}')
                close_status = False
        else:    
            windows = driver.window_handles
            for i in range(len(windows)):
                driver.switch_to.window(windows[i])
                driver.close()
        return close_status
    
    def taskkill_driver(self):
        check_output('taskkill /F /im chrome.exe',creationflags=CREATE_NO_WINDOW)
    
    def driver_content(self,driver):
        return driver.page_source
    
    def driver_url(self,driver):
        return driver.current_url
    
    def driver_alert(self,driver,action=0,msg='',msg_delay=1):
        _alert = Alert(driver)
        if action == 0:
            return _alert.accept()
        elif action == 1:
            return _alert.dismiss()
        elif action == 2:
            return _alert.text
        elif action == 3:
            js = f"alert('{msg}')"
            self.run_js(driver,js)
            sleep(msg_delay)
            Alert(driver).accept()
        else:
            return False
    
    def driver_title(self,driver,option=0,new_title='HungHT1890'):
        """
        option
        0 => get window title
        1 => set title
        """
        if option == 0:
            js = 'return document.title'
            return self.run_js(driver,js)
        elif option == 1:
            js = f'return document.title = "{new_title}"'
            return self.run_js(driver,js)
        else:
            return False
        
        
            
            
    
    """ => close and switch
        lấy số tab hiện có
        mặc định khi lấy -> len sẽ = 1 nếu chỉ có 1 tab 
        mà 1 tab thì index = 0
        trong khi tham số truyền vào là 1
        => sẽ lỗi
        cần so sáng nếu số tab hiện có > số tab truyền vào + 1
        => chuyển / đóng  => tab có index
        nếu không thì return False
        """
    
    "quit tab hoặc toàn bộ driver"
    def quit_driver(self,driver,tab_index:int =0,max_get_tab = 30):
        windows = []
        close_status = True
        if tab_index != 0:
            windows = []
            for x in range(max_get_tab,0,-1):
                windows = driver.window_handles
                if len(windows) >= (tab_index + 1):
                    driver.switch_to.window(windows[tab_index])
                    driver.quit()
                    driver.switch_to.window(windows[0])
                    break
                
                print(f'Wait {x-1} seconds for close tab {tab_index}',end='\r')
                sleep(1)
                
            if len(windows) < (tab_index + 1):
                print(f'\nNo Exist Tab {tab_index}')
                close_status = False
        else:    
            windows = driver.window_handles
            for i in range(len(windows)):
                driver.switch_to.window(windows[i])
                driver.quit()
        return close_status
    
    "chuyển sang cửa sổ"
    def switch_tab(self,driver,tab_index:int = 0,max_get_tab=30):
        status_switch = False
        windows = driver.window_handles
        if tab_index != 0:
            for x in range(max_get_tab,0,-1):
                windows = driver.window_handles
                if len(windows) >= (tab_index + 1):
                    driver.switch_to.window(windows[tab_index])
                    status_switch = True
                    break
                
                print(f'Wait {x-1} seconds for switch tab {tab_index}',end='\r')
                sleep(1)    
            if len(windows) < (tab_index + 1):
                print(f'\nNot Exist Tab {tab_index}')
        else:
            if len(windows)> tab_index + 1:
                driver.switch_to.window(windows[tab_index])
                status_switch = True
                
            else:
                print(f'You are in tab {tab_index}')
            
            
        return status_switch
    
    def scroll_height(self,driver):
        js = 'return document.body.scrollHeight'
        return self.run_js(driver,js)
    
    def scroll_to(self,driver,value=0,to=0):
        scroll_status = True
        """
        0: top
        1: bottom
        2: end
        3: scroll to value (to in function)
        
        """
        scroll_height = self.scroll_height(driver)
        # kéo đến đầu trang
        if value == 0:
            self.run_js(driver,f"window.scrollTo(0, 0)")
        #kéo đến giữa trang 
        elif value == 1:
            bottom = int(scroll_height/2)
            js = f'window.scrollTo(0, {bottom})'
            self.run_js(driver,js)
        
        # kéo đến cuối trang
        elif value == 2:
            self.run_js(driver,f'window.scrollTo(0, {scroll_height})')
            
        # kéo đến vị trí chỉ định
        elif value == 3:
            js = f'window.scrollTo(0, {to})'
            self.run_js(driver,js)

        else:
            print(f'Wrong Option => 0: Top \n1:Botton\n2:End')
            scroll_status = False
            
        return scroll_status
    
    def get_cookies(self,driver,option=0):
        """
        0 => lấy cookie dạng như ở chrome
        1 => lấy cookie dạng dict
        
        """
       
        if option == 0:
            cookie_list = []
            for cookie in (driver.get_cookies()):
                name = cookie['name']
                value = cookie['value']
                cookie_list.append(name + '=' + value)
            return ';'.join(cookie_list)
        else:
            cookie = driver.get_cookies()
            return cookie
    
    def set_cookie(self,driver,cookies,separator=';'):
        status_set_cookie = True
        if type(cookies) == str:
            cookies_extract = cookies.split(separator)
            for cookie in cookies_extract:
                extract = cookie.split('=')
                if len(extract) > 1:
                    name = extract[0].strip()
                    value = extract[1:]
                    if len(value) > 1:
                        value = '='.join(value)
                    else:
                        value = ''.join(value).strip()
                    driver.add_cookie({'name' : name, 'value' : value})
                    
        elif type(cookies) == list:
            for cookie in cookies:
                if type(cookie) == dict:
                    if 'name' in cookie and 'value' in cookie:
                        driver.add_cookie({'name' : name, 'value' : value})
                    
        elif type(cookies) == dict:
            if 'name' in cookie and 'value' in cookie:
                driver.add_cookie({'name' : name, 'value' : value})
        else:
            status_set_cookie = False
        
        return status_set_cookie
    def get_element(self,driver,find_type=By.XPATH,find_value='',time_out=15):
        """ => LẤY ELEMENT <=
        find_type: tìm kiếm dạng nào xpath hay class hay name hay id
        find_value: là giá trị dể tìm kiếm => xpath hay id hoặc classname
        """
        return WebWait(driver,time_out).until(EC.presence_of_element_located((find_type,find_value)))
    
    def get_elements(self,driver,find_type=By.XPATH,find_value='',time_out=15):
        """ => LẤY TOÀN BỘ ELEMENT <=
        find_type: tìm kiếm dạng nào xpath hay class hay name hay id
        find_value: là giá trị dể tìm kiếm => xpath hay id hoặc classname
        """
        return WebWait(driver,time_out).until(EC.presence_of_all_elements_located((find_type,find_value)))
    
    def get_element_text(self,driver,find_type=By.XPATH,find_value=''):
        "LẤY ELEMENT TEXT"
        return self.get_element(driver,find_type,find_value).text
    
    
    def get_element_attribute(self,driver,find_type=By.XPATH,find_value='',get_attribute=''):
        "LẤY THUỘC TÍNH CỦA ELEMENT"
        return self.get_element(driver,find_type,find_value).get_attribute(get_attribute)
    
    
    def get_screen_shot(self,driver,full=True,b64=False,file_image='screen.png',find_type=By.XPATH,find_value='//*'):
        "FULL: TRUE => CHỤP FULL MÀN HÌNH , False => chụp theo element"
        if full:
            if b64:
                return driver.get_screenshot_as_base64()
            driver.save_screenshot(file_image)
        else:
            element = self.get_element(driver,find_type,find_value)
            if b64:
                return element.screenshot_as_base64()
            element.screenshot(file_image)
    
    def element_sendkeys(self,driver,send_type=0,send_data='',find_type=By.XPATH,find_value='',has_delay=False,delay_time=0.2):
        """
        send_type: 0 => sendkeys thường
                   1 => sendkeys dùng actionchains
                   3 =: send key dùng js
        """
        send_key_status = True
        element = self.get_element(driver,find_type,find_value)
        
        if has_delay:
            for data in str(send_data): 
                if send_type == 0:
                    element.send_keys(data)
                
                # không nên dùng vì element bị giới hạn sẽ làm data bị ghi đè
                elif send_type == 1:
                    ActChain(driver).move_to_element(to_element=element).click().send_keys(data).perform()
                    
                    # không nên dùng khi sử dụng delay 
                elif send_type == 2:
                    driver.execute_script("arguments[0].setAttribute('value', '" + data +"')", element)
                else:
                    send_key_status = False
                sleep(delay_time)
                
        else:
            data = str(send_data)
            if send_type == 0:
                element.send_keys(data)
            elif send_type == 1:
                ActChain(driver).move_to_element(to_element=element).click().send_keys(data).perform()
            elif send_type == 2:
                driver.execute_script("arguments[0].setAttribute('value', '" + data +"')", element)
                
            else:
                send_key_status = False
                
        element_value = element.get_attribute("value")
        if element_value != send_data:
            send_key_status = False
        
        return send_key_status
    
            
    def element_lick(self,driver,find_type=By.XPATH,find_value='',click_type=0,count_click=1,click_delay=0.5):
        element = self.get_element(driver,find_type,find_value)
        click_status = True
        if count_click == 0:
            count_click += 1
            
        for i in range(count_click):
            if click_type == 0:
                element.click()
            elif click_type == 1:
                ActChain(driver).move_to_element(to_element=element).click().perform()
            
            elif click_type == 2:
                js = "arguments[0].click();"
                driver.execute_script(js,element)
            else:
                click_status = False
            if count_click > 1:
                sleep(click_delay)
        return click_status
    
    def element_submit(self,driver,find_type=By.XPATH,find_value='',click_type=0,count_click=1,click_delay=0.5):
        element = self.get_element(driver,find_type,find_value)
        click_status = True
        if count_click == 0:
            count_click += 1
            
        for i in range(count_click):
            if click_type == 0:
                element.submit()
            elif click_type == 1:
                ActChain(driver).move_to_element(to_element=element).click().perform()
            
            elif click_type == 2:
                js = "arguments[0].submit();"
                driver.execute_script(js,element)
            else:
                click_status = False
            if count_click > 1:
                sleep(click_delay)
        return click_status
    
    def element_select(self,driver,find_type=By.XPATH,find_value='',select_type=0,select_value=0):
        """
        select type: 0 => select by xpath , class_name , name , id
                     1 => select by 
                    #  not done
        """
        
        select_status = self.get_element(driver,find_type,find_value).click()
    
    def element_checker(self,diver,find_type=By.XPATH,find_value='',check_type=0):
        """ => check type <= 
        0 => check element is display
        1 => check element is enable
        2 => check element is selected
        3 => check element location
        4 => check element size
        
        """
        element = self.get_element(driver,find_type,find_value)
        if check_type == 0:
            return element.is_displayed()
        elif check_type == 1:
            return element.is_enabled()
        elif check_type == 2:
            return element.is_selected()
        elif check_type == 3:
            location = element.location
            return (location['x'],location['y'])
        elif check_type == 4:
            size = element.size
            return (size['width'],size['height'])
        else:
            return 'WRONG_OPTION'
    
    def swith_iframe(self,driver,find_type=By.XPATH,find_value=''):
        "switch to iframe"
        WebWait(driver).until(EC.frame_to_be_available_and_switch_to_it((find_type,find_value)))
        
    def switch_default(self,driver):
        "switch to page defaut content => exit iframe"
        driver.switch_to.default_content()
    
    def element_remove(self,driver,find_type=By.XPATH,find_value='',element_index=0,remove_all=False):
        """
        element_index: int => element index in list of elements
        remove_all: true => remove all elements
        
        """
        elements = self.get_elements(driver,find_type,find_value)
        remove_status = True
        if remove_all:
            for element in elements:
                js = "return arguments[0].remove();"
                driver.execute_script(js,element)
        else:
            if element_index == 0:
                js = "return arguments[0].remove();"
                driver.execute_script(js,elements[element_index])
            else:
                if len(elements) > (element_index + 1):
                    js = "return arguments[0].remove();"
                    driver.execute_script(js,elements[element_index])
                else:
                    remove_status = False
        return remove_status
    
                    
    
    
    
            
    
        
        
                    
                    
                    
    
            
            
            
    
            
            
        
    
    
    

if __name__ == '__main__':
    url = 'https://facebook.com'
    email = 'hungsaki2003@gmail.com'
    user_xpath = '//*[@id="email"]'
    
    seleSupport = HungHT1890Sele()
    driver = seleSupport.chrome_setup()
    seleSupport.open_url(driver,url)
    seleSupport.driver_title(driver,option=1)
    input("Enter to close")
    driver.close()