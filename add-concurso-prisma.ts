import { PrismaClient } from '@prisma/client';
import fs from 'fs';

const prisma = new PrismaClient();

async function main() {
    const data = JSON.parse(fs.readFileSync('concurso.json', 'utf-8'));

    for (const item of data) {
        const { estado, titulo, subtitulo, concursos } = item;
        const newState = await prisma.estado.create({
            data: {
                estado,
                titulo,
                subtitulo,
                concursos: {
                    create: concursos.map((concurso: any) => ({
                        orgao: concurso.orgao,
                        vagas: concurso.vagas,
                        previsto: concurso.previsto
                    }))
                }
            }
        });

        console.log(`Estado ${newState.estado} com concursos criado com sucesso.`);
    }
}

main()
    .then(() => {
        console.log('Importação concluída.');
        prisma.$disconnect();
    })
    .catch((error) => {
        console.error('Erro na importação:', error);
        prisma.$disconnect();
    });
