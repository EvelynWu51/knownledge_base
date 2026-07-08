# processor/import_processor/nodes/node_entry.py
import logging
from pathlib import Path

from processor.import_processor.base import BaseNode
from processor.import_processor.exceptions import StateFieldError, FileProcessingError, ValidationError
from processor.import_processor.state import ImportGraphState


class NodeEntry(BaseNode):
    """
    入口节点：任务分发
    """

    name = "node_entry"

    def process(self, state: ImportGraphState):
        logging.info(f"{self.name}开始执行……")

        #判断路径是否为空
        import_file_path = state.get("import_file_path")
        if not import_file_path:
            raise StateFieldError(field_name='import_file_path',expected_type=str)

        #将文件路径转换为Path对象
        import_file_path_obj = Path(import_file_path)

        #判断Path对象文件是否存在
        if not import_file_path_obj.exists():
            logging.info("文件路径为空")
            raise FileProcessingError(message=f"文件{import_file_path_obj.name}不存在")

        #判断文件后缀名,设置状态：是否启用pdf/md读取，pdf/md路径
        if import_file_path_obj.suffix == ".pdf":
            logging.info("文件类型为pdf")
            state['is_pdf_read_enabled'] = True
            state['pdf_path'] = import_file_path
        elif import_file_path_obj.suffix == ".md":
            logging.info("文件类型为md")
            state['is_md_read_enabled'] = True
            state['md_path'] = import_file_path
        else:
            logging.info("文件格式不支持")
            raise ValidationError(message=f"文件的后缀格式{import_file_path_obj.suffix}不支持")


        #提取文件名作为标题
        state['file_title'] = import_file_path_obj.stem

        #返回更新后的state
        return state







