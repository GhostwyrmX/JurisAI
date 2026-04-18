from services.rag_service import rag_service

print('Testing search for Section 302...')
results = rag_service.search_similar_sections('Section 302 IPC', top_k=5)
print('Results:', results)

for result in results:
    section_num = result['section']['section_number']
    title = result['section']['title']
    score = result['score']
    print(f'Section {section_num}: {title} (score: {score})')