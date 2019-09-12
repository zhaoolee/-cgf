#-*- coding: UTF-8 -*-  
import os
from PIL import Image
import imageio
 
def analyseImage(path):
    '''
    Pre-process pass over the image to determine the mode (full or additive).
    Necessary as assessing single frames isn't reliable. Need to know the mode 
    before processing all frames.
    '''
    im = Image.open(path)
    results = {
        'size': im.size,
        'mode': 'full',
    }
    try:
        while True:
            if im.tile:
                tile = im.tile[0]
                update_region = tile[1]
                update_region_dimensions = update_region[2:]
                if update_region_dimensions != im.size:
                    results['mode'] = 'partial'
                    break
            im.seek(im.tell() + 1)
    except EOFError:
        pass
    return results
 
 
def processImage(path):
    '''
    Iterate the GIF, extracting each frame.
    '''
    mode = analyseImage(path)['mode']
    
    im = Image.open(path)
 
    i = 0
    p = im.getpalette()
    last_frame = im.convert('RGBA')

    # 生成的列表
    image_list = [];
    
    try:
        while True:
            print ("saving %s (%s) frame %d, %s %s" % (path, mode, i, im.size, im.tile))
            
            '''
            If the GIF uses local colour tables, each frame will have its own palette.
            If not, we need to apply the global palette to the new frame.
            '''
            if not im.getpalette():
                im.putpalette(p)
            
            new_frame = Image.new('RGBA', im.size)
            
            '''
            Is this file a "partial"-mode GIF where frames update a region of a different size to the entire image?
            If so, we need to construct the new frame by pasting it on top of the preceding frames.
            '''
            if mode == 'partial':
                new_frame.paste(last_frame)
            
            new_frame.paste(im, (0,0), im.convert('RGBA'))
            # new_frame.save('%s-%d.png' % (''.join(os.path.basename(path).split('.')[:-1]), i), 'PNG')
            image_list.append(new_frame);
 
            i += 1
            last_frame = new_frame
            im.seek(im.tell() + 1)
    except EOFError:
        pass

    return image_list;

def get_new_list_2(before_list, num):
    before_list_length = len(before_list);
    # 如果总帧数列表不超过限制的帧数,则直接返回
    if(before_list_length<=num):
      return before_list;
    # 如果总帧数列表超过了限制的帧数, 则返回"瘦身"后的列表
    else:
      # 返回新的列表
      after_list = [];
      # 取gif帧的间隔
      gap = len(before_list) // num + 1;
      # 移除帧的列表
      remove_frame_list = [];
      # 移除帧列表的最大长度
      remove_frame_list_max_length = len(before_list) - 300;
      for (f_index, f_value) in enumerate(before_list):
        # 如果移除帧的列表 数量不够
        if(len(remove_frame_list) < remove_frame_list_max_length):
          if(f_index % gap != 0):
            remove_frame_list.append(f_index)



      for (f_index, f_value) in enumerate(before_list):
        print("before_list_len::", len(before_list));
        if(f_index not in remove_frame_list):
          after_list.append(f_value)
        print("after_list_len::", len(after_list));
      ## 为保证更高的流畅性, 如果帧数小于预期帧数, 则补齐
      
      return after_list

# 新的抽取帧的函数
def get_new_list(num_list, n):
    if(n == 0):
      # print(num_list);
      return num_list

    if(len(num_list)<=n):
      # print(num_list);
      return num_list

    before_n = n;
    m = len(num_list)
    # n必须小于num_list的一半
    if(n > (m / 2)):
      n = m - n
    # t是分组
    t = m // n + 1
    # 生成包含n个数组的数组n_len_list
    n_len_list = [];
    for nn in range(n):
        n_len_list.append([])
    tmp_num_list = list(num_list)
    while (len(tmp_num_list) > 0):
      for nl in n_len_list:
        if(len(tmp_num_list) > 0):
          nl.append(tmp_num_list[0])
          tmp_num_list = tmp_num_list[1:]
        else:
          pass


    # 拷贝一份数组
    tmp_n_len_list = list(n_len_list)
    tmp_num_list = list(num_list)

    # 构建新的二维数组
    for (tmp_m_index, tmp_m_value) in enumerate(tmp_n_len_list):
      for (tmp_n_index, tmp_n_value) in enumerate(tmp_m_value):
        tmp_n_len_list[tmp_m_index][tmp_n_index] = tmp_num_list[0]
        tmp_num_list = tmp_num_list[1:]
        
        

    # 生成一长一短两个列表
    long_list = []
    short_list = []

    for n_len_atom in n_len_list:
      short_list = short_list + [n_len_atom[0]]
      long_list = long_list + n_len_atom[1:]

    if(len(long_list) == before_n):
      print(long_list)
      return long_list
    if(len(short_list) == before_n):
      print(short_list)
      return short_list



def create_gif(image_list, gif_name):
    frames = []
    for image_name in image_list:
        frames.append(image_name)
    # Save them as frames into a gif 
    imageio.mimsave(gif_name, frames, 'GIF', duration = 0.1)
    return
 

# 读取同级目录下所有gif
# 获取当前目录下所有md文件
def get_gif_files(md_dir):
    gif_files = [];
    for root, dirs, files in sorted(os.walk(md_dir)):
        for file in files:
            # 获取.gif或.GIF结尾的文件
            if(file.endswith(".gif")or(file.endswith(".GIF"))):
                file_path = os.path.join(root, file)
                print(file_path)
                gif_files.append(file_path)
    return gif_files


def main():
    gif_list = get_gif_files("./");
    for (gif_index, gif_value) in enumerate(gif_list):
      image_list = processImage(gif_value);
      print("===>>>", gif_value);
      new_gif_name = 'new_'+ gif_value.split("/")[-1]
      new_image_list = [];
      # 对数组进行瘦身
      new_image_list = get_new_list(image_list, 300)
      create_gif(new_image_list, new_gif_name);
      # # 删除生成的临时静态图片
      # for image_path in image_list: 
      #     os.remove(image_path);


 
if __name__ == "__main__":
    main()