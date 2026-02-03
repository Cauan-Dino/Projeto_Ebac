Clonar o repositório

clonar o repositorio - git clone https://github.com/Cauan-Dino/Projeto_Ebac

-------------------------------
Iniciar a VM

1. Criar uma VM - podman machine init
2. Iniciar uma VM - podman machine start
3. Execução da imagem - podman-compose build
4. Subir a aplicação - podman-compose up -d

-------------------------------
Finalizar a VM

Para a execução da VM - podman-compose stop

Para a execução da VM e exclui o container - podman-compose down 
Para a execução da VM, exclui o container e os volumes dentro do container - podman-compose down -v
