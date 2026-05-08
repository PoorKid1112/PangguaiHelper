import sys
import io
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import time
import json
import requests
import hashlib
import queue

log_queue = queue.Queue()

def sha256_encrypt(data):
    sha256 = hashlib.sha256()
    sha256.update(data.encode("utf-8"))
    return sha256.hexdigest()

def signzfb(t, url, token):
    return sha256_encrypt(
        "appSecret=Ew+ZSuppXZoA9YzBHgHmRvzt0Bw1CpwlQQtSl49QNhY=&channel=alipay&timestamp=" + t +
        "&token=" + token + "&version=1.60.3&" + url[25:])

def sign(t, url, token):
    return sha256_encrypt(
        "appSecret=nFU9pbG8YQoAe1kFh+E7eyrdlSLglwEJeA0wwHB1j5o=&channel=android_app&timestamp=" + t +
        "&token=" + token + "&version=1.60.3&" + url[25:])

def httprequests(url, token, data, mean, ua):
    t = str(int(time.time() * 1000))
    signs = sign(t, url, token)
    headers = {
        "Authorization": token,
        "Version": "1.60.3",
        "channel": "android_app",
        "phoneBrand": "Redmi",
        "timestamp": t,
        "sign": signs,
        "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
        "Host": "userapi.qiekj.com",
        "Connection": "Keep-Alive",
        "Accept-Encoding": "gzip",
        "User-Agent": ua
    }
    if mean == "get":
        try:
            res = requests.get(url=url, headers=headers, timeout=10)
            if res.status_code == 200:
                res_json = json.loads(res.text)
                if res_json["msg"] == "未登录":
                    log_queue.put(("warn", res_json["msg"]))
                    return None
                return res_json
            else:
                log_queue.put(("error", f"请求出错 {res.status_code}"))
                return None
        except requests.exceptions.Timeout:
            log_queue.put(("warn", "请求超时，即将重新请求"))
            return "timeout"
        except Exception as e:
            log_queue.put(("error", str(e)))
            return None
    elif mean == "post":
        try:
            res = requests.post(url=url, headers=headers, data=data, timeout=10)
            if res.status_code == 200:
                res_json = json.loads(res.text)
                if res_json["msg"] == "未登录":
                    log_queue.put(("warn", res_json["msg"]))
                    return None
                return res_json
            else:
                log_queue.put(("error", f"出错 {res.status_code}"))
                return None
        except requests.exceptions.Timeout:
            log_queue.put(("warn", "请求超时，即将重新请求"))
            return "timeout"
        except Exception as e:
            log_queue.put(("error", str(e)))
            return None

def sy(token, ua):
    url = "https://userapi.qiekj.com/task/queryByType"
    data = {"taskCode": "8b475b42-df8b-4039-b4c1-f9a0174a611a", "token": token}
    res_json = httprequests(url=url, token=token, data=data, mean="post", ua=ua)
    if res_json and res_json.get("code") == 0 and res_json.get("data") == True:
        log_queue.put(("success", "首页浏览成功，获得1积分"))
    else:
        log_queue.put(("warn", f"首页浏览失败: {res_json}"))

def qd(token, ua):
    url = "https://userapi.qiekj.com/signin/doUserSignIn"
    data = {"activityId": "600001", "token": token}
    res_json = httprequests(url=url, token=token, data=data, mean="post", ua=ua)
    try:
        if res_json and res_json["code"] == 0:
            log_queue.put(("success", "签到成功，获得积分 " + str(res_json["data"]["totalIntegral"])))
        elif res_json and res_json["code"] == 33001:
            log_queue.put(("info", "当天已经签过到了哦～"))
        else:
            log_queue.put(("warn", f"签到出错: {res_json}"))
    except Exception as e:
        log_queue.put(("error", f"签到异常: {e}"))

def zfbtask(token, ua):
    url = "https://userapi.qiekj.com/task/completed"
    t = str(int(time.time() * 1000))
    signs = signzfb(t, url, token)
    headers = {
        'Authorization': token,
        'Version': '1.60.3',
        'channel': 'alipay',
        'phoneBrand': 'Redmi',
        'timestamp': t,
        'sign': signs,
        'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
        'Host': 'userapi.qiekj.com',
        'Accept-Encoding': 'gzip',
        'User-Agent': ua
    }
    data = {"taskCode": 9, "token": token}
    try:
        res = requests.post(url=url, headers=headers, data=data, timeout=10)
        res_json = json.loads(res.text)
        if res_json["code"] == 0 and res_json["data"] == True:
            return (True, "任务成功", res_json)
        else:
            return (False, res_json.get("msg", "未知错误"), res_json)
    except Exception as e:
        return (False, f"接口请求异常：{str(e)}", None)

def tx(token, taskCode, ua):
    url = "https://userapi.qiekj.com/task/completed"
    data = {"taskCode": taskCode, "token": token}
    return httprequests(url=url, token=token, data=data, mean="post", ua=ua)

def appvideo(token, i, ua):
    url = "https://userapi.qiekj.com/task/completed"
    data = {"taskCode": 2, "token": token}
    res_json = httprequests(url=url, token=token, data=data, mean="post", ua=ua)
    if res_json and res_json.get('code') == 0 and res_json.get('data') == True:
        log_queue.put(("success", f"第{i}次 APP视频任务完成"))
        return "t"
    return "f"

def getusername(token, ua):
    url = "https://userapi.qiekj.com/user/info"
    data = {"token": token}
    res_json = httprequests(url=url, data=data, token=token, mean="post", ua=ua)
    try:
        if res_json and res_json["code"] == 0:
            name = res_json["data"]["userName"] or "（未设置昵称）"
            log_queue.put(("title", f"━━━  {name}  ━━━"))
        else:
            log_queue.put(("warn", f"获取用户名失败: {res_json}"))
    except:
        log_queue.put(("warn", f"获取用户名异常"))

def solt(token, ua):
    url = "https://userapi.qiekj.com/shielding/query"
    data = {"shieldingResourceType": "1", "token": token}
    res_json = httprequests(url=url, data=data, token=token, mean="post", ua=ua)
    log_queue.put(("info", f"屏蔽查询: {res_json}"))

def run_zfb_video_task(token, ua):
    max_video_count = 50
    max_verify_wait = 120
    poll_interval = 10
    verify_tips_shown = False
    unverify_keywords = ["未验证", "请先在APP完成验证", "需要登录", "验证失效", "请打开APP验证", "获取异常"]

    for num in range(max_video_count):
        is_success, err_msg, res_json = zfbtask(token=token, ua=ua)
        if is_success:
            log_queue.put(("success", f"第{num+1}次 支付宝视频任务完成"))
            time.sleep(15)
            verify_tips_shown = False
            continue

        is_unverify = False
        if err_msg:
            is_unverify = any(keyword in err_msg for keyword in unverify_keywords)
        if not is_unverify and res_json:
            is_unverify = any(keyword in res_json.get("msg", "") for keyword in unverify_keywords)

        if is_unverify and not verify_tips_shown:
            log_queue.put(("warn", f"⚠ 检测到支付宝视频任务需要APP验证！"))
            log_queue.put(("warn", f"请在 {max_verify_wait} 秒内打开APP完成验证..."))
            verify_tips_shown = True
            wait_elapsed = 0
            while wait_elapsed < max_verify_wait:
                time.sleep(poll_interval)
                wait_elapsed += poll_interval
                check_success, _, _ = zfbtask(token=token, ua=ua)
                if check_success:
                    log_queue.put(("success", "检测到验证成功，继续执行！"))
                    curr_success, _, _ = zfbtask(token=token, ua=ua)
                    if curr_success:
                        log_queue.put(("success", f"第{num+1}次 支付宝视频任务完成"))
                    time.sleep(15)
                    verify_tips_shown = False
                    break
            if wait_elapsed >= max_verify_wait and verify_tips_shown:
                log_queue.put(("warn", f"超过 {max_verify_wait} 秒未完成验证，暂停支付宝视频任务"))
                break
        else:
            log_queue.put(("warn", f"支付宝视频任务失败：{err_msg}，任务已达上限或接口异常，终止"))
            break

notfin = ["7328b1db-d001-4e6a-a9e6-6ae8d281ddbf", "e8f837b8-4317-4bf5-89ca-99f809bf9041",
          "65a4e35d-c8ae-4732-adb7-30f8788f2ea7", "73f9f146-4b9a-4d14-9d81-3a83f1204b74",
          "12e8c1e4-65d9-45f2-8cc1-16763e710036"]

def run_all_tasks(tokens, ua, stop_event):
    for tk_val in tokens:
        if stop_event.is_set():
            log_queue.put(("warn", "任务已被用户终止"))
            break
        getusername(token=tk_val, ua=ua)
        time.sleep(1)

        url = "https://userapi.qiekj.com/user/balance"
        data = {"token": tk_val}
        res_json = httprequests(url=url, data=data, token=tk_val, mean="post", ua=ua)
        yesterday = res_json['data']['integral'] if res_json else 0
        time.sleep(1)

        qd(token=tk_val, ua=ua)
        solt(tk_val, ua)
        log_queue.put(("info", "3s后开始执行任务..."))
        time.sleep(3)

        sy(token=tk_val, ua=ua)
        time.sleep(1)

        url = "https://userapi.qiekj.com/task/list"
        data = {"token": tk_val}
        res_json = httprequests(url=url, token=tk_val, data=data, mean="post", ua=ua)
        items = []
        try:
            if res_json and res_json["code"] == 0:
                items = res_json["data"]["items"]
            else:
                log_queue.put(("warn", f"获取任务列表失败: {res_json}"))
        except Exception as e:
            log_queue.put(("error", f"获取任务列表异常: {e}"))

        for item in items:
            if stop_event.is_set():
                break
            if item['completedStatus'] == 0 and item["taskCode"] not in notfin:
                log_queue.put(("info", f"──── 开始任务：{item['title']} ────"))
                for num in range(item["dailyTaskLimit"]):
                    if stop_event.is_set():
                        break
                    res_json = tx(token=tk_val, taskCode=item["taskCode"], ua=ua)
                    if res_json and res_json.get("code") == 0 and res_json.get("data") == True:
                        time.sleep(10)
                    else:
                        log_queue.put(("warn", f"任务执行出错: {res_json}"))
                        time.sleep(10)
                log_queue.put(("success", f"✓ {item['title']} 任务完成"))
                time.sleep(5)

        for num in range(20):
            if stop_event.is_set():
                break
            flag = appvideo(token=tk_val, i=num+1, ua=ua)
            if flag == "f":
                break
            time.sleep(15)

        run_zfb_video_task(tk_val, ua)

        time.sleep(3)
        url = "https://userapi.qiekj.com/user/balance"
        data = {"token": tk_val}
        res_json = httprequests(url=url, data=data, token=tk_val, mean="post", ua=ua)
        if res_json:
            total = res_json['data']['integral']
            today = total - yesterday
            log_queue.put(("success", f"📊 总积分：{total}  今日获得：{today}"))
        log_queue.put(("info", "所有任务均已完成，开始下一个账号...\n"))
        time.sleep(3)

    log_queue.put(("done", "✅ 全部账号任务执行完毕！"))


# ─────────────────────────────────────────────────────────
#  GUI 主界面
# ─────────────────────────────────────────────────────────
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("胖乖生活 · 积分助手")
        self.geometry("760x680")
        self.resizable(True, True)
        self.configure(bg="#0f1117")

        self.stop_event = threading.Event()
        self.task_thread = None

        self._build_ui()
        self._poll_log()

    def _build_ui(self):
        # ── 标题栏 ──
        header = tk.Frame(self, bg="#0f1117")
        header.pack(fill="x", padx=20, pady=(18, 0))

        tk.Label(header, text="胖乖生活  积分助手", font=("微软雅黑", 20, "bold"),
                 fg="#f0c040", bg="#0f1117").pack(side="left")
        tk.Label(header, text="v1.0", font=("微软雅黑", 10),
                 fg="#555566", bg="#0f1117").pack(side="left", padx=8, pady=6)

        # ── 分隔线 ──
        tk.Frame(self, bg="#2a2a3a", height=1).pack(fill="x", padx=20, pady=10)

        # ── Token 输入区 ──
        lf1 = tk.LabelFrame(self, text="  Token（每行一个，支持多账号）  ",
                             font=("微软雅黑", 10), fg="#aaaacc", bg="#0f1117",
                             bd=1, relief="solid", highlightbackground="#2a2a3a")
        lf1.pack(fill="x", padx=20, pady=(0, 10))

        self.token_text = tk.Text(lf1, height=5, font=("Consolas", 10),
                                  bg="#161622", fg="#e0e0ff", insertbackground="#f0c040",
                                  relief="flat", bd=8, wrap="none")
        self.token_text.pack(fill="x", padx=4, pady=4)

        token_hint = tk.Label(lf1, text="提示：多个 Token 请每行粘贴一个",
                              font=("微软雅黑", 9), fg="#555566", bg="#0f1117")
        token_hint.pack(anchor="w", padx=8, pady=(0, 4))

        # ── UA 输入区 ──
        lf2 = tk.LabelFrame(self, text="  User-Agent  ",
                             font=("微软雅黑", 10), fg="#aaaacc", bg="#0f1117",
                             bd=1, relief="solid", highlightbackground="#2a2a3a")
        lf2.pack(fill="x", padx=20, pady=(0, 10))

        self.ua_entry = tk.Text(lf2, height=3, font=("Consolas", 9),
                                bg="#161622", fg="#b0c8e8", insertbackground="#f0c040",
                                relief="flat", bd=8, wrap="char")
        self.ua_entry.insert("1.0", "")
        self.ua_entry.pack(fill="x", padx=4, pady=4)

        # ── 按钮组 ──
        btn_frame = tk.Frame(self, bg="#0f1117")
        btn_frame.pack(fill="x", padx=20, pady=(0, 10))

        self.run_btn = tk.Button(btn_frame, text="▶  开始执行任务", font=("微软雅黑", 11, "bold"),
                                 bg="#f0c040", fg="#0f1117", relief="flat", bd=0,
                                 padx=24, pady=8, cursor="hand2",
                                 activebackground="#e0b030", activeforeground="#0f1117",
                                 command=self._start_tasks)
        self.run_btn.pack(side="left", padx=(0, 10))

        self.stop_btn = tk.Button(btn_frame, text="■  停止", font=("微软雅黑", 11),
                                  bg="#2a2a3a", fg="#ff6666", relief="flat", bd=0,
                                  padx=20, pady=8, cursor="hand2",
                                  activebackground="#3a2a3a", activeforeground="#ff8888",
                                  command=self._stop_tasks, state="disabled")
        self.stop_btn.pack(side="left", padx=(0, 10))

        self.clear_btn = tk.Button(btn_frame, text="清空日志", font=("微软雅黑", 10),
                                   bg="#1e1e2e", fg="#888899", relief="flat", bd=0,
                                   padx=16, pady=8, cursor="hand2",
                                   activebackground="#2a2a3a", activeforeground="#aaaacc",
                                   command=self._clear_log)
        self.clear_btn.pack(side="left")

        # ── 状态指示 ──
        self.status_var = tk.StringVar(value="就绪")
        self.status_label = tk.Label(btn_frame, textvariable=self.status_var,
                                     font=("微软雅黑", 9), fg="#555566", bg="#0f1117")
        self.status_label.pack(side="right", padx=4)

        # ── 日志输出区 ──
        lf3 = tk.LabelFrame(self, text="  运行日志  ",
                             font=("微软雅黑", 10), fg="#aaaacc", bg="#0f1117",
                             bd=1, relief="solid")
        lf3.pack(fill="both", expand=True, padx=20, pady=(0, 16))

        self.log_box = scrolledtext.ScrolledText(
            lf3, font=("Consolas", 10), bg="#0a0a14", fg="#ccccdd",
            relief="flat", bd=8, state="disabled", wrap="word",
            insertbackground="#f0c040"
        )
        self.log_box.pack(fill="both", expand=True, padx=4, pady=4)

        # 日志颜色 tag
        self.log_box.tag_config("success", foreground="#4ade80")
        self.log_box.tag_config("warn",    foreground="#facc15")
        self.log_box.tag_config("error",   foreground="#f87171")
        self.log_box.tag_config("info",    foreground="#94a3b8")
        self.log_box.tag_config("title",   foreground="#f0c040", font=("Consolas", 11, "bold"))
        self.log_box.tag_config("done",    foreground="#34d399", font=("Consolas", 11, "bold"))
        self.log_box.tag_config("time",    foreground="#44445a")

    def _log(self, level, msg):
        self.log_box.config(state="normal")
        ts = time.strftime("%H:%M:%S")
        self.log_box.insert("end", f"[{ts}]  ", "time")
        self.log_box.insert("end", msg + "\n", level)
        self.log_box.see("end")
        self.log_box.config(state="disabled")

    def _poll_log(self):
        try:
            while True:
                level, msg = log_queue.get_nowait()
                self._log(level, msg)
                if level == "done":
                    self._on_tasks_done()
        except queue.Empty:
            pass
        self.after(100, self._poll_log)

    def _start_tasks(self):
        raw_tokens = self.token_text.get("1.0", "end").strip()
        ua = self.ua_entry.get("1.0", "end").strip()

        if not raw_tokens:
            messagebox.showwarning("提示", "请先输入 Token！")
            return
        if not ua:
            messagebox.showwarning("提示", "请先输入 User-Agent！")
            return

        tokens = [t.strip() for t in raw_tokens.splitlines() if t.strip()]
        self.stop_event.clear()

        self.run_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.status_var.set(f"运行中  ·  {len(tokens)} 个账号")
        self.status_label.config(fg="#4ade80")

        self._log("info", f"共 {len(tokens)} 个账号，开始执行...")

        self.task_thread = threading.Thread(
            target=run_all_tasks, args=(tokens, ua, self.stop_event), daemon=True)
        self.task_thread.start()

    def _stop_tasks(self):
        self.stop_event.set()
        self._log("warn", "正在停止，等待当前步骤完成...")
        self.stop_btn.config(state="disabled")
        self.status_var.set("停止中...")
        self.status_label.config(fg="#facc15")

    def _on_tasks_done(self):
        self.run_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.status_var.set("就绪")
        self.status_label.config(fg="#555566")

    def _clear_log(self):
        self.log_box.config(state="normal")
        self.log_box.delete("1.0", "end")
        self.log_box.config(state="disabled")


if __name__ == "__main__":
    app = App()
    app.mainloop()
