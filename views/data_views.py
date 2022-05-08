# -- coding: utf-8 --

from flask import Flask, Blueprint, render_template, redirect, request
import json
from datetime import datetime
import os
# 블루프린트 객체 생성, 현재 파일은 app.py에 모듈로 추가되어 사용됨.
bp = Blueprint('users_views', __name__, url_prefix='/')

# $$$$$$$$$$$$$데이터를 보존하기 위해 json 파일로 읽고 쓰는 부분$$$$$$
# 실행하면 json 파일에서 기존 데이터를 가져와 리스트에 넣음.
json_file = "static/data/data.json"
try:
    with open(json_file, "r") as f:
        data_json = json.load(f)
    data_list = data_json["data"]
    print('파일읽기 성공')

except:
    data_list = []
    print('빈파일입니다.')


def dumptoJson():  # json파일에 수시로 업데이트 저장하는 함수 호출
    data_dic = {"data": data_list}
    with open(json_file, "w") as f:
        json.dump(data_dic, f, indent=4)

############ 여기서 부터가 CRUD를  처리하는 부분 #######################

############ 데이터를 생성하는 부분 ###############


@bp.route('/create', methods=['GET', 'POST'])  # 입력하는 부분
def create():
    if request.method == 'POST':  # 폼의 데이터를 가지고 post방식으로 들어옴.
        id = datetime.now().strftime("%y%m%d%H%M%S")  # 시간을 고유id값으로 사용
        name = request.form['name']
        title = request.form['title']   # 태그의 name속성의 값을 사용함.
        content = request.form['content']
        file = request.files['file']
        if file:
            dir_path = 'static/images'
            file_name = "img"+id+".jpg"
            file_path = os.path.join(dir_path, file_name)
            file.save(file_path)
        else:
            file_name = ""

        temp = {"id": id, "name": name, "title": title,
                "content": content, "image": file_name}  # 딕셔녀리형식{키:값}
        data_list.append(temp)  # 딕셔너리를 리스트 항목으로 추가 [{키:값},{키,값}]

        dumptoJson()  # json파일에 저장 업데이트하는 함수 호출
        return redirect('/list')  # 다른 주소로 이동하는 리디렉션
    else:  # get방식으로 들어오면 입력화면을 보여줌
        return render_template('create.html')

############ 목록을 보여주는 부분  #############


@bp.route('/list')
def list():  # 데이터 전달만함
    return render_template('list.html', datatojson=data_list)

############ 각 항목의 세부내용을 보여주는 부분 ######


@ bp.route('/read/<id>')
def read(id):
    selected = None
    for data in data_list:  # data_list에 있는 항목을 하나씩 data변수에 저장하며 반복
        if id == data['id']:  # id가 같으면 현재항목을 selected에 저장
            selected = data
            break    # 해당 항목 찾으면 더이상 반복할 필요없으므로 반복문을 빠져 나옴
    return render_template('read.html', selected=selected)

############업데이트 , 삭제와 생성의 조합 ##############


@bp.route('/update/<id>', methods=['GET', 'POST'])
def update(id):
    selected = None
    idx = None
    for data in data_list:
        if id == data['id']:
            selected = data
            idx = data_list.index(data)  # 해당리스트 항목의 인덱스 번호 확인
            break
    if request.method == 'POST':  # post 방식으로 왔을때만 수정
        data_list[idx]['name'] = request.form['name']
        data_list[idx]['title'] = request.form['title']
        data_list[idx]['content'] = request.form['content']
        file = request.files['file']
        if file:
            dir_path = './static/images'
            file_name = "img"+id+".jpg"
            data_list[idx]['image'] = file_name
            file_path = os.path.join(dir_path, file_name)
            file.save(file_path)

        dumptoJson()  # json파일에 저장 업데이트하는 함수 호출
        return redirect('/list')
    else:  # get방식으로 들어오면 페이지로 연결과 내용 보여줌
        return render_template('update.html', selected=selected)

############삭제, 주소로 접근해서 못지우게 POST방식으로만 처리 #########


@bp.route('/delete/<id>', methods=['POST'])
def delete(id):
    if request.method == 'POST':
        for data in data_list:  # data는 딕션너리형식
            if id == data['id']:
                dir_path = 'static/images'
                file_name = data['image']
                file_path = os.path.join(dir_path, file_name)
                if os.path.isfile(file_path):  # 파일 유무확인 후 삭제
                    os.remove(file_path)

                data_list.remove(data)  # 리스트의 해당항목을 삭제함
                break
        dumptoJson()
    return redirect('/list')  # 삭제하고 리스트보여주기
