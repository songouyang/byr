#!/usr/bin/env python3
import re
import argparse
import requests


class Byr:
    def __init__(self, username=None, password=None):
        self.username = username
        self.password = password
        assert self.username and self.password, "用户名和密码不能为空"
        self.session = requests.Session()

    def __enter__(self):
        files = {
            "username": (None, self.username),
            "password": (None, self.password),
        }
        rsp = self.session.post("https://bbs.byr.cn/n/b/auth/login.json", files=files, timeout=10)
        assert rsp.ok and rsp.json().get("success")
        print("login success")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        rsp = self.session.get("https://bbs.byr.cn/n/b/auth/logout.json", timeout=10)
        assert rsp.ok and rsp.json().get("success")
        print("logout success")

    def get_post_info(self, post_url):
        pattern = re.compile(r"https://bbs.byr.cn/n/article/(\w+)/(\d+)")
        match = pattern.match(post_url)
        assert match, "不符合规范的文章链接"
        board_name = match.group(1)
        gid = match.group(2)
        url = f"https://bbs.byr.cn/n/b/article/{board_name}/{gid}.json"
        rsp = self.session.get(url, params=dict(page=1), timeout=10)
        assert rsp.ok and rsp.json().get("success")
        print(f"get post【{post_url}】 detail info success")
        return rsp.json()

    def comment(self, post_url, content):
        post_info = self.get_post_info(post_url)
        post_title = post_info["data"]["title"]
        subject = f"Re: {post_title}"
        print(f"post title: {post_title}, subject: {subject}")

        board_name = post_info["data"]["board"]["name"]
        post_id = post_info["data"]["gid"]
        print(f"board name: {board_name}, post id: {post_id}")

        prereply = f"https://bbs.byr.cn/n/b/article/{board_name}/prereply/{post_id}.json"
        prereply_rsp = self.session.post(prereply, timeout=10)
        if prereply_rsp.json().get("message"):
            print(f"由于【{prereply_rsp.json()['message']}】，不发表评论")
            return

        url = f"https://bbs.byr.cn/n/b/article/{board_name}/post/{post_id}.json"
        files = {
            "subject": (None, subject),
            "content": (None, content),
        }
        rsp = self.session.post(url, files=files, timeout=10)
        assert rsp.ok and rsp.json().get("success"), "评论失败"
        print(f"reply content【{content}】to post【{post_url}】 success")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("username", type=str)
    parser.add_argument("password", type=str)
    args = parser.parse_args()
    
    with Byr(args.username, args.password) as byr:
        byr.comment("https://bbs.byr.cn/n/article/ParttimeJob/882238", "UP")
