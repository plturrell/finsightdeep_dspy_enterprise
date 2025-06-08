"""
SAP HANA Cloud vector database integration for DSPy.

This module provides integration with SAP HANA Cloud as a vector database 
for efficient retrieval of documents using vector embeddings.
"""

import logging
import os
from functools import lru_cache
from typing import Any, Dict, List, Optional, Union

import numpy as np
import dspy

try:
    from hdbcli import dbapi
    HAS_HDBCLI = True
except ImportError:
    HAS_HDBCLI = False
    
from dspy.retrieve.retrieve import Retrieve

logger = logging.getLogger(__name__)


class HanaVectorStore:
    """
    SAP HANA Cloud Vector Store implementation for DSPy.
    
    This class provides methods to interact with a SAP HANA Cloud database
    for storing and retrieving document embeddings.
    """
    
    def __init__(
        self, 
        connection: Optional[Any] = None,
        host: Optional[str] = None,
        port: int = 443,
        user: Optional[str] = None,
        password: Optional[str] = None,
        schema: str = "PUBLIC",
        table: str = "VECTOR_STORE",
        dimension: int = 1536,
    ):
        """
        Initialize the SAP HANA Cloud Vector Store.
        
        Args:
            connection: Optional existing dbapi connection to SAP HANA Cloud
            host: SAP HANA Cloud host (not needed if connection is provided)
            port: SAP HANA Cloud port (default: 443)
            user: SAP HANA Cloud username (not needed if connection is provided)
            password: SAP HANA Cloud password (not needed if connection is provided)
            schema: Database schema (default: PUBLIC)
            table: Table name for vector storage (default: VECTOR_STORE)
            dimension: Vector dimension (default: 1536 for OpenAI embeddings)
        """
        if not HAS_HDBCLI:
            raise ImportError(
                "The 'hdbcli' package is required to use the SAP HANA Cloud Vector Store. "
                "Install it with 'pip install hdbcli'."
            )
        
        self.connection = connection
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.schema = schema
        self.table = table
        self.dimension = dimension
        self.table_fqn = f"{self.schema}.{self.table}"
        
        # Connect to the database if no connection was provided
        if self.connection is None:
            self._connect()
            
        # Initialize the table if it doesn't exist
        self._init_table()
    
    def _connect(self):
        """Establish connection to SAP HANA Cloud."""
        if not all([self.host, self.user, self.password]):
            # Try to get connection parameters from environment variables
            self.host = self.host or os.environ.get("SAP_HANA_HOST")
            self.port = self.port or int(os.environ.get("SAP_HANA_PORT", 443))
            self.user = self.user or os.environ.get("SAP_HANA_USER")
            self.password = self.password or os.environ.get("SAP_HANA_PASSWORD")
            self.schema = self.schema or os.environ.get("SAP_HANA_SCHEMA", "PUBLIC")
            self.table = self.table or os.environ.get("SAP_HANA_TABLE", "VECTOR_STORE")
            
        if not all([self.host, self.user, self.password]):
            raise ValueError(
                "Missing connection parameters for SAP HANA Cloud. "
                "Please provide host, user, and password."
            )
            
        try:
            self.connection = dbapi.connect(
                address=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                sslValidateCertificate=False
            )
            logger.info(f"Connected to SAP HANA Cloud at {self.host}:{self.port}")
        except Exception as e:
            logger.error(f"Failed to connect to SAP HANA Cloud: {e}")
            raise
    
    def _init_table(self):
        """Create vector table if it doesn't exist."""
        try:
            cursor = self.connection.cursor()
            
            # Check if table exists
            table_check_query = f"""
            SELECT COUNT(*) FROM SYS.TABLES 
            WHERE SCHEMA_NAME = ? AND TABLE_NAME = ?
            """
            cursor.execute(table_check_query, (self.schema, self.table))
            exists = cursor.fetchone()[0] > 0
            
            if not exists:
                logger.info(f"Creating vector table {self.table_fqn}")
                
                # Create vector table
                create_table_query = f"""
                CREATE TABLE {self.table_fqn} (
                    id NVARCHAR(100) PRIMARY KEY,
                    text NCLOB,
                    vector REAL ARRAY({self.dimension}),
                    metadata NCLOB
                )
                """
                cursor.execute(create_table_query)
                
                # Create vector index
                create_index_query = f"""
                CREATE INDEX {self.table}_vector_idx ON {self.table_fqn}(vector) 
                INVERTED INDIVIDUAL
                """
                cursor.execute(create_index_query)
                
                logger.info(f"Created vector table and index in {self.table_fqn}")
            else:
                logger.info(f"Using existing vector table {self.table_fqn}")
                
            cursor.close()
            
        except Exception as e:
            logger.error(f"Failed to initialize vector table: {e}")
            raise
    
    def add_documents(self, documents: List[Dict[str, Any]], embeddings: List[List[float]]):
        """
        Add documents and their embeddings to the vector store.
        
        Args:
            documents: List of documents with at least 'id' and 'text' fields
            embeddings: List of vector embeddings corresponding to the documents
        """
        if len(documents) != len(embeddings):
            raise ValueError("Number of documents must match number of embeddings")
        
        try:
            cursor = self.connection.cursor()
            
            # Prepare the insert query
            insert_query = f"""
            UPSERT {self.table_fqn} (id, text, vector, metadata)
            VALUES (?, ?, ?, ?) 
            """
            
            # Insert documents and embeddings
            for doc, emb in zip(documents, embeddings):
                doc_id = doc.get("id")
                text = doc.get("text", "")
                metadata = doc.get("metadata", "{}")
                
                cursor.execute(insert_query, (doc_id, text, emb, metadata))
            
            self.connection.commit()
            cursor.close()
            
            logger.info(f"Added {len(documents)} documents to {self.table_fqn}")
            
        except Exception as e:
            logger.error(f"Failed to add documents: {e}")
            raise
    
    def similarity_search(
        self, 
        query_vector: List[float], 
        k: int = 5, 
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Perform similarity search using the query vector.
        
        Args:
            query_vector: Vector embedding of the query
            k: Number of results to return (default: 5)
            filter_dict: Optional filter conditions for metadata
            
        Returns:
            List of documents with similarity scores
        """
        try:
            cursor = self.connection.cursor()
            
            # Build the query
            where_clause = ""
            params = [k]  # First param is k
            
            if filter_dict:
                # Simple filtering for demonstration purposes
                # In production, you'd want to parse the filter_dict and build a more complex WHERE clause
                where_clause = " WHERE metadata LIKE ? "
                params.append(f"%{filter_dict}%")
            
            query = f"""
            SELECT id, text, metadata, 
                   COSINE_SIMILARITY(vector, ?) AS score
            FROM {self.table_fqn}
            {where_clause}
            ORDER BY score DESC
            LIMIT ?
            """
            
            # Execute query with query vector as parameter
            cursor.execute(query, [query_vector, *params])
            
            # Fetch results
            results = []
            for row in cursor.fetchall():
                results.append({
                    "id": row[0],
                    "text": row[1],
                    "metadata": row[2],
                    "score": row[3]
                })
            
            cursor.close()
            return results
            
        except Exception as e:
            logger.error(f"Failed to perform similarity search: {e}")
            raise
    
    def delete_document(self, doc_id: str):
        """
        Delete a document from the vector store by ID.
        
        Args:
            doc_id: ID of the document to delete
        """
        try:
            cursor = self.connection.cursor()
            delete_query = f"DELETE FROM {self.table_fqn} WHERE id = ?"
            cursor.execute(delete_query, (doc_id,))
            self.connection.commit()
            cursor.close()
            
            logger.info(f"Deleted document {doc_id} from {self.table_fqn}")
            
        except Exception as e:
            logger.error(f"Failed to delete document: {e}")
            raise
    
    def close(self):
        """Close the database connection."""
        if hasattr(self, 'connection') and self.connection:
            self.connection.close()
            logger.info("Closed SAP HANA Cloud connection")


class SAPHanaRM(Retrieve):
    """
    Retrieval module for SAP HANA Cloud vector database integration.
    
    This class provides a DSPy retrieval module that integrates with
    SAP HANA Cloud for vector search operations.
    """
    
    def __init__(
        self,
        k: int = 5,
        vector_store: Optional[HanaVectorStore] = None,
        host: Optional[str] = None,
        port: int = 443,
        user: Optional[str] = None,
        password: Optional[str] = None,
        schema: str = "PUBLIC",
        table: str = "VECTOR_STORE",
        dimension: int = 1536,
        callbacks=None,
    ):
        """
        Initialize the SAP HANA Cloud Retrieval Module.
        
        Args:
            k: Number of documents to retrieve (default: 5)
            vector_store: Optional pre-configured HanaVectorStore instance
            host: SAP HANA Cloud host (not needed if vector_store is provided)
            port: SAP HANA Cloud port (default: 443)
            user: SAP HANA Cloud username (not needed if vector_store is provided)
            password: SAP HANA Cloud password (not needed if vector_store is provided)
            schema: Database schema (default: PUBLIC)
            table: Table name for vector storage (default: VECTOR_STORE)
            dimension: Vector dimension (default: 1536 for OpenAI embeddings)
            callbacks: Optional callbacks for tracking operations
        """
        super().__init__(k=k, callbacks=callbacks)
        
        # Use provided vector store or create a new one
        self.vector_store = vector_store or HanaVectorStore(
            host=host,
            port=port,
            user=user,
            password=password,
            schema=schema,
            table=table,
            dimension=dimension,
        )
        
        # Cache for storing embeddings
        self._embedding_cache = {}
    
    @lru_cache(maxsize=1024)
    def _get_embedding(self, text: str) -> List[float]:
        """
        Get embedding for text, using cache to avoid redundant computations.
        
        Args:
            text: Text to get embedding for
            
        Returns:
            Vector embedding as list of floats
        """
        import dspy
        
        # Get the embedder from DSPy settings
        embedder = dspy.settings.embedder
        if embedder is None:
            raise ValueError("No embedder configured in DSPy settings")
        
        embedding = embedder.encode([text])[0]
        return embedding.tolist()
    
    def forward(self, query: str, k: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Retrieve documents from SAP HANA Cloud based on query.
        
        Args:
            query: The search query
            k: Number of results to return (overrides instance k if provided)
            
        Returns:
            List of retrieved documents with similarity scores
        """
        k = k or self.k
        query_vector = self._get_embedding(query)
        
        results = self.vector_store.similarity_search(query_vector, k=k)
        
        # Format results for DSPy
        formatted_results = []
        for idx, result in enumerate(results):
            formatted_results.append(dspy.Example(
                id=result["id"],
                long_text=result["text"],
                score=result["score"],
                metadata=result["metadata"],
            ))
        
        return formatted_results
    
    def __del__(self):
        """Close the vector store connection when the object is deleted."""
        if hasattr(self, 'vector_store'):
            try:
                self.vector_store.close()
            except:
                pass  # Ignore errors on cleanup