#!/usr/bin/env python
"""
Test script for verifying SAP HANA Cloud Vector Store connectivity in DSPy.
"""

import argparse
import json
import logging
import os
import sys
from typing import List, Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

def parse_args():
    parser = argparse.ArgumentParser(description="Test SAP HANA Cloud Vector Store connectivity")
    parser.add_argument(
        "--host", 
        default=os.environ.get("SAP_HANA_HOST"),
        help="SAP HANA Cloud host"
    )
    parser.add_argument(
        "--port", 
        type=int,
        default=int(os.environ.get("SAP_HANA_PORT", "443")),
        help="SAP HANA Cloud port"
    )
    parser.add_argument(
        "--user", 
        default=os.environ.get("SAP_HANA_USER"),
        help="SAP HANA Cloud username"
    )
    parser.add_argument(
        "--password", 
        default=os.environ.get("SAP_HANA_PASSWORD"),
        help="SAP HANA Cloud password"
    )
    parser.add_argument(
        "--schema", 
        default=os.environ.get("SAP_HANA_SCHEMA", "PUBLIC"),
        help="SAP HANA Cloud schema"
    )
    parser.add_argument(
        "--table", 
        default=os.environ.get("SAP_HANA_TABLE", "VECTOR_STORE"),
        help="SAP HANA Cloud table"
    )
    parser.add_argument(
        "--test-data",
        action="store_true",
        help="Insert test data into the vector store"
    )
    parser.add_argument(
        "--query",
        type=str,
        help="Test query to run against the vector store"
    )
    return parser.parse_args()

def test_connection(args):
    """Test connection to SAP HANA Cloud."""
    logger.info(f"Testing connection to SAP HANA Cloud at {args.host}:{args.port}")
    
    try:
        from hdbcli import dbapi
        
        # Connect to SAP HANA
        connection = dbapi.connect(
            address=args.host,
            port=args.port,
            user=args.user,
            password=args.password,
            sslValidateCertificate=False
        )
        
        # Get SAP HANA version
        cursor = connection.cursor()
        cursor.execute("SELECT VERSION FROM SYS.M_DATABASE")
        version = cursor.fetchone()[0]
        cursor.close()
        
        logger.info(f"✅ Successfully connected to SAP HANA Cloud (Version: {version})")
        
        return connection
    
    except ImportError:
        logger.error("❌ Failed to import hdbcli. Install with 'pip install hdbcli'")
        return None
    except Exception as e:
        logger.error(f"❌ Failed to connect to SAP HANA Cloud: {e}")
        return None

def test_vector_store(connection, args):
    """Test the SAP HANA Cloud Vector Store implementation."""
    if connection is None:
        logger.error("Cannot test vector store without connection")
        return False
    
    try:
        # Check if the vector store module is available
        sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
        
        try:
            from dspy.retrieve.sap_hana_rm import HanaVectorStore, SAPHanaRM
            logger.info("✅ Successfully imported SAP HANA Cloud Vector Store modules")
        except ImportError as e:
            logger.error(f"❌ Failed to import SAP HANA Cloud Vector Store modules: {e}")
            return False
        
        # Initialize the vector store
        vector_store = HanaVectorStore(
            connection=connection,
            schema=args.schema,
            table=args.table,
            dimension=1536
        )
        
        logger.info(f"✅ Successfully initialized SAP HANA Cloud Vector Store with table {args.schema}.{args.table}")
        
        # Test data insertion if requested
        if args.test_data:
            logger.info("Inserting test data into the vector store...")
            
            # Simple test data with mock embeddings
            documents = [
                {"id": "doc1", "text": "SAP HANA Cloud is a powerful database platform", "metadata": '{"source": "test"}'},
                {"id": "doc2", "text": "Vector search enables semantic retrieval in DSPy", "metadata": '{"source": "test"}'},
                {"id": "doc3", "text": "NVIDIA GPUs accelerate AI workloads efficiently", "metadata": '{"source": "test"}'},
            ]
            
            # Generate random embeddings for testing
            import numpy as np
            embeddings = [np.random.rand(1536).tolist() for _ in range(len(documents))]
            
            # Add documents to vector store
            vector_store.add_documents(documents, embeddings)
            logger.info(f"✅ Successfully added {len(documents)} test documents to the vector store")
        
        # Test query if provided
        if args.query:
            logger.info(f"Testing query: '{args.query}'")
            
            # Generate a random embedding for the query (since we don't have a real embedding model here)
            import numpy as np
            query_vector = np.random.rand(1536).tolist()
            
            # Perform similarity search
            results = vector_store.similarity_search(query_vector, k=2)
            
            logger.info(f"✅ Successfully performed similarity search")
            logger.info(f"Retrieved {len(results)} documents:")
            
            for i, result in enumerate(results):
                logger.info(f"Result {i+1}:")
                logger.info(f"  - ID: {result.get('id')}")
                logger.info(f"  - Text: {result.get('text')}")
                logger.info(f"  - Score: {result.get('score')}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to test vector store: {e}")
        return False

def main():
    args = parse_args()
    
    # Print connection parameters (masked password)
    masked_password = "********" if args.password else "None"
    logger.info(f"SAP HANA Cloud Connection Parameters:")
    logger.info(f"  - Host: {args.host}")
    logger.info(f"  - Port: {args.port}")
    logger.info(f"  - User: {args.user}")
    logger.info(f"  - Password: {masked_password}")
    logger.info(f"  - Schema: {args.schema}")
    logger.info(f"  - Table: {args.table}")
    
    # Test connection
    connection = test_connection(args)
    
    if connection:
        # Test vector store
        vector_store_ok = test_vector_store(connection, args)
        
        # Close connection
        connection.close()
        logger.info("Closed SAP HANA Cloud connection")
        
        if vector_store_ok:
            logger.info("✅ SAP HANA Cloud Vector Store tests completed successfully")
            return 0
    
    logger.error("❌ SAP HANA Cloud Vector Store tests failed")
    return 1

if __name__ == "__main__":
    sys.exit(main())