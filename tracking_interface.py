import tkinter as tk
from tkinter import *
import threading
from selenium.webdriver.support.ui import Select
import time
import pandas as pd
from selenium import webdriver
import re
from datetime import date


class SampleApp(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self._frame = None
        self.switch_frame(StartPage)

    def switch_frame(self, frame_class):
        """Destroys current frame and replaces it with a new one."""
        new_frame = frame_class(self)
        if self._frame is not None:
            self._frame.destroy()

        self._frame = new_frame
        self._frame.pack()


class StartPage(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg="#C4C4C4", padx=40, pady=10, width=880, height=500)
        master.geometry("700x350")
        # master.iconbitmap("favicon.ico")
        master.title("Tracking Automation")
        master.resizable(False, False)

        start_header = Label(self, text="Please fill in all fields as required ", bg="#C5C3C3")
        start_header.grid(padx=5, pady=(0, 10), sticky=W, row=0)
        global label1
        frame1 = LabelFrame(self, padx=10, pady=20, bg="#ffffff", borderwidth=0, highlightthickness=0, relief='ridge')
        frame1.grid(padx=5, pady=0, sticky=W, row=1)
        frame11 = LabelFrame(frame1, padx=0, pady=5, bg="#ffffff", borderwidth=0, highlightthickness=0, relief='ridge')
        frame11.grid(row=0, column=0, padx=(0, 20), pady=10, )
        frame12 = LabelFrame(frame1, padx=0, pady=0, bg="#ffffff", borderwidth=0, highlightthickness=0, relief='ridge')
        frame12.grid(row=0, column=1)
        frame13 = LabelFrame(self, padx=0, pady=0, bg="#ffffff", borderwidth=0, highlightthickness=0, relief='ridge')
        frame13.grid(row=2, column=0, padx=0, pady=0)
        label1 = Label(frame11, text="number of days you want to calculate difference between ", bg="#ffffff")
        label1.grid(row=0, column=0, padx=5, pady=7, sticky=W)
        global my_entry1
        my_entry1 = Entry(frame11, width=50, highlightthickness=1, background="white")

        my_entry1.grid(row=1, column=0, padx=5, pady=2, sticky=W, ipadx=70, ipady=5)

        label2 = Label(frame11, text="inter file name", bg="#ffffff")
        label2.grid(row=2, column=0, padx=5, pady=7, sticky=W)
        global my_entry2
        my_entry2 = Entry(frame11, width=50, highlightthickness=1, background="white")

        my_entry2.grid(row=3, column=0, padx=5, pady=2, sticky=W, ipadx=70, ipady=5)

        global calc
        calc = False

        def calc_func():
            global calc
            calc = True

        def switch_driver(driver, path):
            driver.quit()
            time.sleep(10)
            driver = webdriver.Chrome(executable_path=path)
            return driver

        def get_links(driver, page_link):
            ii = 0
            path = r"C:/chromedriver.exe"
            while ii < 2:
                try:
                    for i in range(2):
                        driver.get(page_link)
                    ii+=1
                    time.sleep(2)
                    driver.find_element_by_id("add-to-cart-button").click()
                    time.sleep(3)
                    driver.find_element_by_id("hlb-view-cart-announce").click()
                    time.sleep(3)
                    sel = Select(driver.find_element_by_name("quantity"))
                    sel.select_by_value("10")
                    time.sleep(2)
                    input = driver.find_element_by_name("quantityBox")
                    input.send_keys("999")
                    time.sleep(2)
                    update = driver.find_element_by_class_name(
                        "a-button a-button-primary a-button-small sc-update-link".replace(" ",
                                                                                          ".")).find_element_by_tag_name(
                        "a")
                    update.click()
                    time.sleep(4)
                    try:
                        input_text = driver.find_element_by_class_name("a-popover-content").text
                        print(input_text)
                        input_int = int(re.search(r'\d+', input_text).group())
                    except:
                        input_text = driver.find_element_by_class_name(
                            "sc-quantity-update-message a-spacing-top-mini".replace(" ", ".")).text
                        print(input_text)
                        input_int = int(re.search(r'\d+', input_text).group())
                    delete = driver.find_element_by_class_name(
                        "a-size-small sc-action-delete".replace(" ", ".")).find_element_by_tag_name("input")
                    delete.click()
                    time.sleep(2)
                    return driver,input_int
                except:
                    while True:
                        try:
                            driver = switch_driver(driver, path)
                            driver.get("https://www.amazon.com/")
                            print(driver.title)
                            break
                        except:
                            pass

            else:
                return driver,0

        def get_data(col_n, file_name):
            global calc
            df = pd.read_excel(file_name + ".xlsx")
            counter = 0
            path = r"chromedriver.exe"
            driver = webdriver.Chrome(executable_path=path)
            today = date.today()
            df[str(today)] = 0
            for i in range(df.shape[0]):
                today = date.today()
                # df[str(today)] = 0
                page_link = df.loc[i, "links"]
                driver,df.loc[i, str(today)] = get_links(driver, page_link)
                print(df.loc[i, str(today)])

                if i % 10 == 0 and i != 0:
                    while True:
                        try:
                            driver = switch_driver(driver, path)
                            driver.get("https://www.amazon.com/")
                            print(driver.title)
                            break
                        except:
                            pass

            main_data_frame = df
            main_data_frame.to_csv(file_name + ".csv", index=False)
            writer = pd.ExcelWriter(file_name + '.xlsx', engine='xlsxwriter',
                                    options={'strings_to_urls': False, "index": False})
            main_data_frame.to_excel(writer, index=False)
            writer.close()
            if calc:
                col_n = int(col_n) + 1
                calc_df = df
                col_name = "calc_" + str(today)
                columns_to_drop = []
                for col in calc_df.columns:
                    if "calc" in col:
                        columns_to_drop.append(col)
                        print(col)
                try:
                    calc_df = calc_df.drop(columns_to_drop, axis=1)
                except:
                    print("we passed columns drop")

                calc_df[col_name] = calc_df[calc_df.columns[-col_n]] - calc_df[calc_df.columns[-1]]
                df[col_name] = calc_df[col_name]
                print("col_name", col_name)
                # print(calc_df[calc_df.columns[-col_n]])
                main_data_frame = df
                main_data_frame = main_data_frame.sort_values(by=[col_name], ascending=False).reset_index()
                main_data_frame.to_csv(file_name + ".csv", index=False)
                writer = pd.ExcelWriter(file_name + '.xlsx', engine='xlsxwriter',
                                        options={'strings_to_urls': False, "index": False})
                main_data_frame.to_excel(writer, index=False)
                writer.close()

        def running_function():
            s1 = threading.Thread(target=get_data, args=[my_entry1.get(), my_entry2.get()])
            s1.start()

        remember_button = Checkbutton(frame13, text="calculate diff", command=calc_func, bg="#ffffff")
        remember_button.grid(row=0, column=0, padx=69, pady=2, sticky=W, ipadx=5, ipady=5)

        start_button = Button(frame13, text="start", command=running_function, bg="#35A11B",
                              borderwidth=2, highlightthickness=0, relief='ridge')
        start_button.grid(row=0, column=2, padx=70, pady=2, sticky=E, ipadx=40, ipady=5)

        footer = Label(self, text="All rights reserved to Ali_Nasser foundation 2021-2022", bg="#C5C3C3")
        footer.grid(row=3, column=0, padx=5, pady=(10, 0), sticky=W)


if __name__ == "__main__":
    app = SampleApp()
    app.mainloop()
