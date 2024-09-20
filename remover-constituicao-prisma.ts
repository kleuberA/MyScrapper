import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

async function main() {
    // Deletar os conteúdos (Content)
    await prisma.content.deleteMany({});
    console.log('Todos os conteúdos deletados.');

    // Deletar os artigos (Article)
    await prisma.article.deleteMany({});
    console.log('Todos os artigos deletados.');

    // Deletar as leis (Law)
    await prisma.law.deleteMany({
        where: {
            createdAt: {
                gte: new Date(new Date().setDate(new Date().getDate() - 1)) // Registros criados nas últimas 24 horas
            }
        }
    });
    console.log('Todas as leis deletadas.');
}

main()
    .catch((e) => {
        console.error(e);
        process.exit(1);
    })
    .finally(async () => {
        await prisma.$disconnect();
    });
