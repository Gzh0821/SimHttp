#   Copyright 2023 Gaozih/Gzh0821 https://github.com/Gzh0821
#
#     Licensed under the Apache License, Version 2.0 (the "License");
#     you may not use this file except in compliance with the License.
#     You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.

import imghdr
import json
import os
import pathlib
import re
import subprocess

from server.ConfigTool import GlobalConfig as Config


class ByteHandler:
    @classmethod
    def is_image_file(cls, file_path) -> bool:
        # 使用 imghdr 判断文件是否为图片
        file_type = imghdr.what(file_path)
        return file_type is not None

    @classmethod
    def read_byte(cls, file_path) -> bytes:
        with open(file_path, 'rb') as file:
            image_bytes = file.read()
        return image_bytes


class FileReader:
    access_file_type = {'.html': 'text/html; charset=utf-8', '.css': 'text/css; charset=utf-8',
                        '.js': 'application/javascript; charset=utf-8', '.json': 'text/json',
                        '.jpg': 'image/jpeg', '.png': 'image/png', '.webp': 'image/webp',
                        '.ico': 'image/x-icon',
                        '.pycgi': 'text/html; charset=utf-8', '.plcgi': 'text/html; charset=utf-8'}
    byte_type = {'.jpg', '.png', '.webp', '.ico'}
    cgi_type = {'.pycgi', '.plcgi'}

    @classmethod
    def read(cls, request_path: str, dynamic_para: dict[str:str] = None) \
            -> tuple[int, str | bytes, str]:
        """
        读取文件内容
        :param request_path:
        :param dynamic_para:
        :return:
        """
        if request_path == '/teapot':
            return 418, 'I\'m a teapot', 'text/plain; charset=utf-8'
        web_dir = Config.get('web_dir')
        file_path = f'./{web_dir}{request_path}'
        status = 200
        file_type = pathlib.Path(file_path).suffix
        if file_type == '':
            if file_path[-1] != '/':
                file_path += '/'
            file_path += Config.get('home_page')
            file_type = pathlib.Path(file_path).suffix
        print(f'请求文件：{file_path}')
        # 检查是否禁止访问
        if file_type not in cls.access_file_type:
            status = 403
            file_path = f'./{web_dir}/403.html'
        else:
            # 检查文件是否存在
            file_exist = os.path.exists(file_path)
            if not file_exist:
                file_path = f'./{web_dir}/404.html'
                status = 404
        print(f'读取文件：{file_path}')
        file_type = pathlib.Path(file_path).suffix
        # 读取文件全部内容
        if file_type in cls.byte_type:
            content = ByteHandler.read_byte(file_path)
        else:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            # 处理动态内容
            if file_type in cls.cgi_type and content.startswith('<!--{{dynamic}}-->'):
                dynamic_pattern = r"<!--{%(\w+)%}-->"
                content = content[len('<!--{{dynamic}}-->'):]
                if dynamic_para is not None:
                    content = re.sub(dynamic_pattern,
                                     lambda match: dynamic_para.get(match.group(1), match.group(0)),
                                     content)
                    # result = re.sub(pattern, lambda match: dictionary.get(match.group(1), ''), text)
                else:
                    content = re.sub(dynamic_pattern, '', content, 0)
        # 特殊页面处理
        if file_path.endswith('404_page.html'):
            status = 404
        elif file_path.endswith('403_page.html'):
            status = 403
        return status, content, cls.access_file_type[file_type]

    @classmethod
    def read_400(cls, request_path: str = '/400.html') -> tuple[str, str]:
        web_dir = Config.get('web_dir')
        with open(f'./{web_dir}{request_path}', 'r', encoding='utf-8') as file:
            content = file.read()
        return content, cls.access_file_type['.html']


class ExecHandler:
    cgi_type_dict = {'.pycgi': ('.py', 'python'), '.plcgi': ('.pl', 'perl')}

    @classmethod
    def handle(cls, path: str, content: str, method: str) -> tuple[dict[str, str], bool]:
        web_dir = Config.get('web_dir')
        file_path = f'./{web_dir}{path}'
        file_type = pathlib.Path(file_path).suffix
        if file_type not in cls.cgi_type_dict:
            return {}, False
        cgi_file_path = file_path[:file_path.rfind(file_type)] + cls.cgi_type_dict[file_type][0]
        cgi_exec_command = cls.cgi_type_dict[file_type][1]
        try:
            with open(cgi_file_path, 'r', encoding='utf-8') as file:
                flag_cont = file.readline()
                if flag_cont.startswith('# {%ONLY POST%}') and method != 'POST':
                    return {}, True
        except FileNotFoundError:
            return {}, True
        try:
            output = subprocess.check_output([cgi_exec_command, cgi_file_path, content], stderr=subprocess.STDOUT)
            print(content)
        except subprocess.CalledProcessError:
            return {}, True
        out_text = output.decode("utf-8")
        print(out_text)
        out_dict: dict[str, str] = json.loads(out_text)
        return out_dict, True
