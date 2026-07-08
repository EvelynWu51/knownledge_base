import logging

from langgraph.constants import END
from langgraph.graph import StateGraph

from processor.import_processor.nodes.a_node_entry import NodeEntry
from processor.import_processor.nodes.b_node_pdf_to_md import NodePDFToMD
from processor.import_processor.nodes.c_node_md_img import NodeMDImg
from processor.import_processor.nodes.d_node_document_split import NodeDocumentSplit
from processor.import_processor.nodes.e_node_item_name_recognition import NodeItemNameRecognition
from processor.import_processor.nodes.f_node_bge_embedding import NodeBGEEmbedding
from processor.import_processor.nodes.g_node_import_milvus import NodeImportMilvus
from processor.import_processor.state import ImportGraphState




class KBImportWorkflow:

    def __init__(self,config=None):
        self._compiled_graph = None

    @property
    def graph(self):
        logging.info("Get Graph")

        if self._compiled_graph is None:
            logging.info("no graph,build new graph")
            self._compiled_graph = self.build_graph
        else:
            logging.info("graph already compiled")

        return self._compiled_graph

    @staticmethod
    def route_after_entry(state:ImportGraphState):
        if state.get("is_pdf_read_enabled"):
            return "node_pdf_to_md"
        elif state.get("is_md_read_enabled"):
            return "node_md_img"
        else:
            return END

    @property
    def build_graph(self):
        """
        Build main graph
        """

        builder = StateGraph(ImportGraphState)

        builder.add_node("node_entry",NodeEntry())
        builder.add_node("node_pdf_to_md", NodePDFToMD())
        builder.add_node("node_md_img", NodeMDImg())
        builder.add_node("node_document_split", NodeDocumentSplit())
        builder.add_node("node_item_name_recognition", NodeItemNameRecognition())
        builder.add_node("node_bge_embedding", NodeBGEEmbedding())
        builder.add_node("node_import_milvus", NodeImportMilvus())

        builder.add_conditional_edges(
            "node_entry",
            self.route_after_entry,
            {
                "node_pdf_to_md":"node_pdf_to_md",
                "node_md_img":"node_md_img",
                END:END
            }
        )
        builder.add_edge("node_pdf_to_md","node_md_img")
        builder.add_edge("node_md_img","node_document_split")
        builder.add_edge("node_document_split", "node_item_name_recognition")
        builder.add_edge("node_item_name_recognition", "node_bge_embedding")
        builder.add_edge("node_bge_embedding", "node_import_milvus")


        graph = builder.compile()
        return graph