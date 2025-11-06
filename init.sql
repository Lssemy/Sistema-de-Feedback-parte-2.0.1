CREATE TABLE feedbacks (
    id SERIAL PRIMARY KEY,
    data_feedback DATE NOT NULL,
    id_curso VARCHAR(100) NOT NULL,
    qualidade_conteudo DECIMAL(2,1) NOT NULL,
    qualidade_instrutor DECIMAL(2,1) NOT NULL,
    recomendacao VARCHAR(50) NOT NULL,
    comentario TEXT
);

-- Inserindo dados iniciais de feedback simulados
INSERT INTO feedbacks (data_feedback, id_curso, qualidade_conteudo, qualidade_instrutor, recomendacao, comentario)
VALUES 
  ('2025-01-15', 'Python Básico', 4.5, 5.0, 'Sim', 'Excelente introdução.'),
  ('2025-01-20', 'Streamlit & Dashboard', 4.0, 4.0, 'Talvez', 'Bom, mas a documentação confunde.'),
  ('2025-02-05', 'Análise de Dados com Pandas', 5.0, 5.0, 'Sim', 'O melhor curso da plataforma!'),
  ('2025-02-12', 'Introdução ao SQL', 3.5, 4.0, 'Sim', 'Conteúdo sólido.'),
  ('2025-03-01', 'Machine Learning Básico', 4.8, 4.9, 'Sim', 'Avançado demais, mas muito completo.'),
  ('2025-03-01', 'Python Básico', 3.0, 3.5, 'Não', 'Achei o ritmo lento.');