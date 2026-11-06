const DELETE_MESSAGE = 'Usuário deletado, mas as matrículas e pagamentos ficaram sujos no banco.';

function createUserController({ userModel, logger }) {
    return {
        async remove(req, res) {
            try {
                await userModel.deleteById(req.params.id);
            } catch (err) {
                logger.error('falha ao excluir usuário', { userId: req.params.id, error: err.message });
            }
            // Contrato preservado (Opção 1): sempre 200 com o texto original (CT-04 e órfãos do F-016 residuais).
            res.send(DELETE_MESSAGE);
        },
    };
}

module.exports = { createUserController };
