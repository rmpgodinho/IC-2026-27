// signal to noise ratio: 10* log10(a**2/delta**2)
// O Erro Quadrático Médio (MSE) é a energia do ruído dividida pelo número de frames


#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <sndfile.h>

int main(int argc, char *argv[]) {
    if (argc != 3) {
        printf("Uso: %s <original.wav> <modificado.wav>\n", argv[0]);
        return 1;
    }

    SNDFILE *file_orig, *file_mod;
    SF_INFO sfinfo_orig = {0};
    SF_INFO sfinfo_mod = {0};

    if ((file_orig = sf_open(argv[1], SFM_READ, &sfinfo_orig)) == NULL) {
        printf("Erro ao abrir ficheiro original: %s\n", sf_strerror(NULL));
        return 1;
    }

    if ((file_mod = sf_open(argv[2], SFM_READ, &sfinfo_mod)) == NULL) {
        printf("Erro ao abrir ficheiro modificado: %s\n", sf_strerror(NULL));
        sf_close(file_orig);
        return 1;
    }

    if (sfinfo_orig.channels != sfinfo_mod.channels || sfinfo_orig.frames != sfinfo_mod.frames) {
        printf("ERRO: Os ficheiros não são compatíveis (canais ou frames diferentes).\n");
        sf_close(file_orig);
        sf_close(file_mod);
        return 1;
    }

    sf_count_t num_frames = sfinfo_orig.frames;
    int channels = sfinfo_orig.channels;

    // Alocação de memória para leitura
    double *data_orig = (double *)malloc(num_frames * channels * sizeof(double));
    double *data_mod = (double *)malloc(num_frames * channels * sizeof(double));

    sf_readf_double(file_orig, data_orig, num_frames);
    sf_readf_double(file_mod, data_mod, num_frames);

    sf_close(file_orig);
    sf_close(file_mod);

    // Estruturas para guardar as métricas exigidas
    // Alocamos (channels + 1) para guardar os dados de cada canal + o canal médio (MID)
    int num_metrics = channels + 1;
    double *signal_energy = (double *)calloc(num_metrics, sizeof(double));
    double *noise_energy = (double *)calloc(num_metrics, sizeof(double));
    double *max_abs_error = (double *)calloc(num_metrics, sizeof(double));

    // Cálculo dos Erros e Energia
    for (sf_count_t i = 0; i < num_frames; i++) {
        double sum_orig = 0.0;
        double sum_mod = 0.0;

        for (int c = 0; c < channels; c++) {
            double orig_sample = data_orig[i * channels + c];
            double mod_sample = data_mod[i * channels + c];
            double error = orig_sample - mod_sample;

            // Acumular energia do sinal e do erro para cada canal
            signal_energy[c] += orig_sample * orig_sample;
            noise_energy[c] += error * error;

            // Atualizar o erro máximo absoluto para cada canal
            if (fabs(error) > max_abs_error[c]) {
                max_abs_error[c] = fabs(error);
            }

            sum_orig += orig_sample;
            sum_mod += mod_sample;
        }

        // canal médio
        double avg_orig = sum_orig / channels;
        double avg_mod = sum_mod / channels;
        double avg_error = avg_orig - avg_mod;

        int avg_idx = channels; // O último índice é o do canal médio
        signal_energy[avg_idx] += avg_orig * avg_orig;
        noise_energy[avg_idx] += avg_error * avg_error;
        
        if (fabs(avg_error) > max_abs_error[avg_idx]) {
            max_abs_error[avg_idx] = fabs(avg_error);
        }
    }

    printf("\n--- Relatório de Comparação (%s vs %s) ---\n\n", argv[1], argv[2]);

    for (int c = 0; c < num_metrics; c++) {
        if (c < channels) {
            printf(">> Canal %d:\n", c);
        } else {
            printf(">> Média dos Canais (MID):\n");
        }

        // MSE
        double mse = noise_energy[c] / num_frames;

        // SNR
        double snr;
        if (noise_energy[c] == 0) {
            snr = INFINITY; // Se não há erro, o SNR é infinito (ficheiros são idênticos)
        } else {
            snr = 10.0 * log10(signal_energy[c] / noise_energy[c]);
        }

        printf("   - Maximum Absolute Error (L-inf): %f\n", max_abs_error[c]);
        printf("   - Average Mean Squared Error (L2): %f\n", mse);
        printf("   - Signal-to-Noise Ratio (SNR): %f dB\n\n", snr);
    }

    free(data_orig);
    free(data_mod);
    free(signal_energy);
    free(noise_energy);
    free(max_abs_error);

    return 0;
}