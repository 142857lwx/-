# 校园图书借阅系统 - 学生登录测试脚本
# 需要先安装selenium和msedgedriver
# pip install selenium
# 下载msedgedriver并将其路径添加到PATH

from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os

def test_student_login():
    results = []
    
    # 配置Edge远程调试模式
    edge_options = Options()
    edge_options.add_argument("--remote-debugging-port=9222")
    edge_options.add_argument("--start-maximized")
    
    # 创建WebDriver (需要msedgedriver在PATH中)
    try:
        driver = webdriver.Edge(options=edge_options)
    except Exception as e:
        print(f"无法启动Edge浏览器: {e}")
        print("请确保已安装msedgedriver并添加到PATH")
        return results
    
    try:
        # 步骤1: 打开登录页面
        print("步骤1: 打开 http://localhost:8080/index.html")
        driver.get("http://localhost:8080/index.html")
        results.append(("打开登录页面", True, "页面加载成功"))
        
        # 等待页面加载
        time.sleep(2)
        
        # 步骤2: 输入用户名
        print("步骤2: 输入用户名 student1")
        username_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@placeholder='请输入用户名']"))
        )
        username_input.clear()
        username_input.send_keys("student1")
        results.append(("输入用户名", True, "用户名已输入"))
        
        # 步骤3: 输入密码
        print("步骤3: 输入密码")
        password_input = driver.find_element(By.XPATH, "//input[@placeholder='请输入密码']")
        password_input.clear()
        password_input.send_keys("password")
        results.append(("输入密码", True, "密码已输入"))
        
        # 步骤4: 点击登录按钮
        print("步骤4: 点击登录按钮")
        login_button = driver.find_element(By.XPATH, "//button[@type='submit' and contains(@class, 'btn-primary')]")
        login_button.click()
        results.append(("点击登录按钮", True, "登录按钮已点击"))
        
        # 等待页面加载
        time.sleep(3)
        
        # 步骤5: 检查是否登录成功
        print("步骤5: 验证登录状态")
        try:
            # 检查是否显示用户名称或侧边栏
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "sidebar"))
            )
            results.append(("登录验证", True, "登录成功，进入仪表盘"))
        except:
            results.append(("登录验证", False, "登录可能失败，未检测到侧边栏"))
        
        # 步骤6: 截取登录后的仪表盘页面截图
        print("步骤6: 截取仪表盘页面截图")
        screenshot_path = os.path.join(os.path.dirname(__file__), "dashboard_screenshot.png")
        driver.save_screenshot(screenshot_path)
        results.append(("截取仪表盘截图", True, f"截图已保存: {screenshot_path}"))
        
        # 步骤7: 进入"图书管理"页面
        print("步骤7: 进入图书管理页面")
        try:
            books_link = driver.find_element(By.XPATH, "//a[@href='#books']")
            books_link.click()
            time.sleep(2)
            
            # 验证图书列表是否正常显示
            table = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "table"))
            )
            results.append(("图书管理页面", True, "图书列表正常显示"))
        except Exception as e:
            results.append(("图书管理页面", False, f"进入失败: {str(e)}"))
        
        # 步骤8: 进入"借阅记录"页面
        print("步骤8: 进入借阅记录页面")
        try:
            borrow_link = driver.find_element(By.XPATH, "//a[@href='#borrow']")
            borrow_link.click()
            time.sleep(2)
            
            # 验证借阅记录表格
            table = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "table"))
            )
            results.append(("借阅记录页面", True, "借阅记录页面正常显示"))
        except Exception as e:
            results.append(("借阅记录页面", False, f"进入失败: {str(e)}"))
        
        # 步骤9: 进入"智能推荐"页面
        print("步骤9: 进入智能推荐页面")
        try:
            recommend_link = driver.find_element(By.XPATH, "//a[@href='#recommend']")
            recommend_link.click()
            time.sleep(2)
            
            # 点击"重新生成推荐"按钮
            regenerate_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//button[contains(text(), '重新生成推荐')]"))
            )
            regenerate_button.click()
            time.sleep(2)
            results.append(("智能推荐页面", True, "成功点击重新生成推荐按钮"))
        except Exception as e:
            results.append(("智能推荐页面", False, f"进入或操作失败: {str(e)}"))
        
        # 步骤10: 进入"阅读统计"页面
        print("步骤10: 进入阅读统计页面")
        try:
            reading_link = driver.find_element(By.XPATH, "//a[@href='#reading']")
            reading_link.click()
            time.sleep(2)
            
            # 验证阅读统计页面元素
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "readingChart"))
            )
            results.append(("阅读统计页面", True, "阅读统计页面正常显示"))
        except Exception as e:
            results.append(("阅读统计页面", False, f"进入失败: {str(e)}"))
        
    except Exception as e:
        print(f"测试过程中发生错误: {e}")
        results.append(("测试异常", False, str(e)))
    
    finally:
        driver.quit()
    
    return results

if __name__ == "__main__":
    print("=" * 60)
    print("校园图书借阅系统 - 学生登录测试")
    print("=" * 60)
    
    results = test_student_login()
    
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    for i, (step, passed, message) in enumerate(results, 1):
        status = "✓ 通过" if passed else "✗ 失败"
        print(f"{i}. {step}: {status}")
        print(f"   详情: {message}")
    
    passed_count = sum(1 for _, passed, _ in results if passed)
    total_count = len(results)
    print(f"\n总计: {passed_count}/{total_count} 项测试通过")
