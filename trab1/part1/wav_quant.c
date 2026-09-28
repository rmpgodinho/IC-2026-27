#include <stdio.h>
#include <math.h>
#include <sndfile.h>
#include <stdlib.h>
//lk = Amin + ∆/2 + k∆
int main(int argc, char *argv[])
{
    SNDFILE *original, *output;
    
    // INICIALIZAÇÃO SEGURA: Limpa todos os campos da estrutura a zero
    SF_INFO sfinfo = {0}; 
    
    int b = 2; // Número de bits para a quantização
    double a_max, delta, a_min;
    double *data;
    sf_count_t num_frames;

    if ((original = sf_open("sample01.wav", SFM_READ, &sfinfo)) == NULL) {
        printf("Error opening input file: %s\n", sf_strerror(NULL));
        return 1;
    }

    // Guardar o número de frames do ficheiro original
    sf_count_t original_frames = sfinfo.frames;

    if (original_frames == 0) {
        printf("ERRO: O ficheiro sample01.wav foi aberto, mas tem 0 segundos de áudio.\n");
        sf_close(original);
        return 1;
    }

    num_frames = sfinfo.frames * sfinfo.channels;
    data = (double *)malloc(num_frames * sizeof(double));

    if (data == NULL) {
        printf("Memory allocation error.\n");
        sf_close(original);
        return 1;
    }

    sf_count_t read_frames = sf_readf_double(original, data, original_frames);

    printf("Frames lidos do original: %ld\n", (long)read_frames);

    sf_close(original);
    
    a_min = -1.0;
    a_max = 1.0;
    
    // Calcula o número total de níveis (2^b)
    int levels = 1 << b;

    // Calcula o delta
    delta = (a_max - a_min) / levels;

    // Quantização
    for (sf_count_t i = 0; i < num_frames; i++) {
        int k = floor((data[i] - a_min) / delta);

        // limites do k
        if (k < 0) k = 0;
        if (k >= levels) k = levels - 1;

        data[i] = a_min + (delta / 2.0) + (k * delta);
    }

    SF_INFO outinfo = sfinfo;
    outinfo.format = SF_FORMAT_WAV | SF_FORMAT_PCM_16;

    if ((output = sf_open("sample01_quant.wav", SFM_WRITE, &outinfo)) == NULL) {
        printf("Error opening output file: %s\n", sf_strerror(NULL));
        free(data);
        return 1;
    }

    sf_count_t written_frames = sf_writef_double(output, data, original_frames);

    printf("Frames escritos no output: %ld\n", (long)written_frames);

    if (written_frames != original_frames) {
        printf("AVISO: Falha na escrita! O ficheiro ficou incompleto.\n");
    }

    sf_close(output);
    free(data);

    return 0;
}