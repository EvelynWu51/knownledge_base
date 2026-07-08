# processor/import_processor/nodes/node_pdf_to_md.py
import json
import logging
from pathlib import Path

from processor.import_processor.base import BaseNode, setup_logging
from processor.import_processor.exceptions import StateFieldError, FileProcessingError
from processor.import_processor.state import ImportGraphState


class NodePDFToMD(BaseNode):
    """
    PDF 转 Markdown 节点：PDF结构化解析
    """

    name = "node_pdf_to_md"

    def process(self, state: ImportGraphState):
        logging.info(f"{self.name}开始执行……")
        pdf_path = state['pdf_path']
        file_dir = state.get('file_dir') or str(Path(pdf_path).parent)

        #1 检查获取相关参数
        pdf_path_obj,output_dir_obj = self._step_1_validata_paths(state)

        #2 获取上传链接并上传文件到mineru服务器
        zip_url = self._step_2_upload_and_poll(pdf_path_obj)

        #3 下载zip压缩文件并解压
        md_path = self._step_3_download_and_extract(zip_url, output_dir_obj, pdf_path_obj.stem)

        #4 读取文件
        with open(md_path,"r",encoding="utf-8") as md_file:
            md_content = md_file.read()

        #5 设置state结果
        state["md_content"] = md_content
        state["md_path"] = md_path
        return state


    def _step_1_validata_paths(self,state: ImportGraphState):


        pdf_path = state['pdf_path']


        # 判断pdf_path是否为空
        if pdf_path is None:
            raise StateFieldError(field_name="pdf_path",expected_type=str)

        pdf_path_obj = Path(pdf_path)
        file_dir = state.get('file_dir') or str(pdf_path_obj.parent)

        #判断file_dir是否为空，为空使用默认值
        if file_dir is None:
            raise StateFieldError(field_name="file_dir", expected_type=str)

        #判断pdf_path_obj是否存在文件
        if not pdf_path_obj.exists():
            raise FileProcessingError(message=f"文件{pdf_path_obj.name}不存在")

        file_dir_obj = Path(file_dir)


        return pdf_path_obj,file_dir_obj


    def _step_2_upload_and_poll(self,pdf_path_obj):
        logging.info("上传轮询中……")
        return "文件上传"

    def _step_3_download_and_extract(self,zip_url,output_dir_obj,output_file_name):
        logging.info("下载解压中……")
        return "下载解压"



if __name__ == "__main__":
    setup_logging()
    node = NodePDFToMD()
    init_state = {"pdf_path":r"C:\Users\Public\Nwt\cache\recv\徐老师\掌柜智库课件0525\掌柜智库课件0525\2.资料\04-设备手册汇总\doc\Aolynk CB304n Cable网桥 用户手册-5W100-整本手册.pdf"}
    result = node(init_state)

    dumps = json.dumps(result, ensure_ascii=False, indent=4)
