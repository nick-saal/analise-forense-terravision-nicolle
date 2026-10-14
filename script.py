def carregar_camada_satelite(lista_altitudes):
    for altitude in lista_altitudes:

        print(f"\nAltitude da câmera: {altitude} metros")

        if altitude > 10000:
            print("Nível de resolução: Baixa resolução")
            print("Carregando o mosaico geral da Terra.")
            print("Renderizando a localização das ilhas e formações insulares no oceano.")

        elif altitude >= 1000:
            print("Nível de resolução: Média resolução")
            print("Carregando o mosaico regional do oceano.")
            print("Renderizando os contornos das ilhas e a área oceânica ao redor.")

        else:
            print("Nível de resolução: Alta resolução")
            print("Carregando imagens detalhadas da região insular.")
            print("Renderizando praias, vegetação, rochas e detalhes do litoral.")


# Lista com cinco altitudes da câmera virtual, em metros
altitudes = [15000, 8000, 3000, 900, 300]

# Executa a função para cada altitude
carregar_camada_satelite(altitudes)
