import chainlit as cl
from PyPDF2 import PdfReader
from io import BytesIO

@cl.on_chat_start
async def start():
    await cl.Message(content="Welcome! Please upload a PDF file to get started.").send()

@cl.on_message
async def main(message: cl.Message):
    # Handle PDF upload
    if message.elements:
        pdf_file = message.elements[0]
        if pdf_file.name.endswith('.pdf'):
            try:
                # Get the bytes content
                pdf_bytes = pdf_file.content
                
                # Create PDF reader object
                pdf_reader = PdfReader(BytesIO(pdf_bytes))
                
                # Extract text from all pages
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                
                # Store the text in session
                cl.user_session.set('pdf_text', text)
                
                # Send confirmation with document stats
                num_pages = len(pdf_reader.pages)
                await cl.Message(
                    content=f"✅ PDF processed successfully!\n\n"
                            f"📄 Number of pages: {num_pages}\n"
                            f"📝 Total characters: {len(text)}\n\n"
                            f"You can now ask questions about the content."
                ).send()
            
            except Exception as e:
                await cl.Message(
                    content=f"❌ Error processing PDF: {str(e)}\n"
                            f"Please make sure you uploaded a valid PDF file."
                ).send()
                return
        else:
            await cl.Message(
                content="❌ Please upload a PDF file (file ending in .pdf)"
            ).send()
            return

    # Handle questions about the PDF content
    else:
        pdf_text = cl.user_session.get('pdf_text')
        if not pdf_text:
            await cl.Message(
                content="⚠️ Please upload a PDF file first!"
            ).send()
            return

        try:
            # Get user's question
            question = message.content.strip().lower()
            
            # Split text into paragraphs and search
            paragraphs = [p.strip() for p in pdf_text.split('\n\n') if p.strip()]
            
            relevant_paragraphs = []
            for para in paragraphs:
                # Simple relevance check - if any word from question appears in paragraph
                question_words = set(question.split())
                para_words = set(para.lower().split())
                if question_words & para_words:  # If there's any overlap
                    relevant_paragraphs.append(para)
            
            if relevant_paragraphs:
                response = "📑 Here are the relevant sections I found:\n\n"
                for i, para in enumerate(relevant_paragraphs[:3], 1):  # Limit to top 3 matches
                    response += f"**Excerpt {i}:**\n{para}\n\n"
                await cl.Message(content=response).send()
            else:
                await cl.Message(
                    content="❓ I couldn't find specific information about that in the document. "
                           "Please try rephrasing your question."
                ).send()
                
        except Exception as e:
            await cl.Message(
                content=f"❌ Error processing your question: {str(e)}"
            ).send()