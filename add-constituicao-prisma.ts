import { PrismaClient } from '@prisma/client';
import fs from 'fs';

const prisma = new PrismaClient();

async function main() {
    // Ler o arquivo JSON
    const data = JSON.parse(fs.readFileSync('constituicao.json', 'utf-8'));

    // Iterar sobre os títulos
    for (const item of data) {
        // Criar ou salvar cada lei (título)
        const law = await prisma.law.create({
            data: {
                titulo: item.titulo,
                nomeTitulo: item.nome_titulo,
                capitulo: item.capitulo || null,
                nomeCapitulo: item.nome_capitulo || null,
                articles: {
                    create: item.artigos.map((artigo: any) => ({
                        artigo: artigo.artigo,
                        contents: {
                            create: artigo.conteudo.map((conteudo: string) => ({
                                texto: conteudo,
                            })),
                        },
                    })),
                },
            },
        });
        console.log(`Lei ${law.titulo} salva com sucesso.`);
    }
}

main()
    .catch((e) => {
        console.error(e);
        process.exit(1);
    })
    .finally(async () => {
        await prisma.$disconnect();
    });
