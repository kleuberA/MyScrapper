-- CreateTable
CREATE TABLE "Estado" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "estado" TEXT NOT NULL,
    "titulo" TEXT NOT NULL,
    "subtitulo" TEXT NOT NULL
);

-- CreateTable
CREATE TABLE "Concurso" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "orgao" TEXT NOT NULL,
    "vagas" TEXT NOT NULL,
    "previsto" BOOLEAN NOT NULL,
    "estadoId" INTEGER NOT NULL,
    CONSTRAINT "Concurso_estadoId_fkey" FOREIGN KEY ("estadoId") REFERENCES "Estado" ("id") ON DELETE RESTRICT ON UPDATE CASCADE
);
