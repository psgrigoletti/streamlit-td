import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from pathlib import Path
from config import (
    SMTP_SERVER,
    SMTP_PORT,
    EMAIL_USER,
    EMAIL_PASSWORD,
    ALERTS_FILE
)


class AlertManager:
    def __init__(self):
        """Inicializa o gerenciador de alertas."""
        self.alerts_file = ALERTS_FILE
        self.alerts = self._load_alerts()
    
    def _load_alerts(self):
        """Carrega os alertas do arquivo CSV."""
        try:
            if Path(self.alerts_file).exists():
                df = pd.read_csv(self.alerts_file)
                df['data_criacao'] = pd.to_datetime(df['data_criacao'])
                return df
        except Exception as e:
            print(f"Erro ao carregar alertas: {str(e)}")
        return pd.DataFrame(columns=[
            'nome', 'email', 'tipo_titulo', 'ano_vencimento',
            'preco_min', 'preco_max', 'taxa_min', 'taxa_max',
            'data_criacao'
        ])
    
    def _save_alerts(self):
        """Salva os alertas no arquivo CSV."""
        try:
            self.alerts.to_csv(self.alerts_file, index=False)
            return True
        except Exception as e:
            print(f"Erro ao salvar alertas: {str(e)}")
            return False
    
    def add_alert(
        self, nome, email, tipo_titulo, ano_vencimento,
        preco_min=None, preco_max=None, taxa_min=None, taxa_max=None
    ):
        """
        Adiciona um novo alerta.
        
        Args:
            nome (str): Nome do usuário
            email (str): Email do usuário
            tipo_titulo (str): Tipo do título do Tesouro Direto
            ano_vencimento (int): Ano de vencimento do título
            preco_min (float, optional): Preço mínimo para alerta
            preco_max (float, optional): Preço máximo para alerta
            taxa_min (float, optional): Taxa mínima para alerta
            taxa_max (float, optional): Taxa máxima para alerta
        """
        new_alert = {
            'nome': nome,
            'email': email,
            'tipo_titulo': tipo_titulo,
            'ano_vencimento': ano_vencimento,
            'preco_min': preco_min,
            'preco_max': preco_max,
            'taxa_min': taxa_min,
            'taxa_max': taxa_max,
            'data_criacao': datetime.now()
        }
        
        self.alerts = pd.concat(
            [self.alerts, pd.DataFrame([new_alert])],
            ignore_index=True
        )
        return self._save_alerts()
    
    def remove_alert(self, index):
        """
        Remove um alerta pelo índice.
        
        Args:
            index (int): Índice do alerta a ser removido
        """
        if 0 <= index < len(self.alerts):
            self.alerts = self.alerts.drop(index).reset_index(drop=True)
            return self._save_alerts()
        return False
    
    def check_alerts(self, df):
        """
        Verifica se algum alerta foi acionado com base nos dados fornecidos.
        
        Args:
            df (pd.DataFrame): DataFrame com os dados do Tesouro Direto
        
        Returns:
            list: Lista de alertas acionados
        """
        alerts_triggered = []
        
        for _, alert in self.alerts.iterrows():
            # Filtrar dados para o tipo e ano de vencimento do alerta
            alert_data = df[
                (df['Tipo Titulo'] == alert['tipo_titulo']) &
                (df['Ano Vencimento'] == alert['ano_vencimento'])
            ]
            
            if not alert_data.empty:
                # Obter dados mais recentes
                latest_data = alert_data.iloc[-1]
                
                # Verificar condições do alerta
                triggered = False
                message = []
                
                if pd.notna(alert['preco_min']) and latest_data['PU Compra Manha'] >= alert['preco_min']:
                    triggered = True
                    message.append(
                        f"Preço atual (R$ {latest_data['PU Compra Manha']:.2f}) "
                        f"acima do mínimo (R$ {alert['preco_min']:.2f})"
                    )
                
                if pd.notna(alert['preco_max']) and latest_data['PU Compra Manha'] <= alert['preco_max']:
                    triggered = True
                    message.append(
                        f"Preço atual (R$ {latest_data['PU Compra Manha']:.2f}) "
                        f"abaixo do máximo (R$ {alert['preco_max']:.2f})"
                    )
                
                if pd.notna(alert['taxa_min']) and latest_data['Taxa Compra Manha'] >= alert['taxa_min']:
                    triggered = True
                    message.append(
                        f"Taxa atual ({latest_data['Taxa Compra Manha']:.2f}%) "
                        f"acima do mínimo ({alert['taxa_min']:.2f}%)"
                    )
                
                if pd.notna(alert['taxa_max']) and latest_data['Taxa Compra Manha'] <= alert['taxa_max']:
                    triggered = True
                    message.append(
                        f"Taxa atual ({latest_data['Taxa Compra Manha']:.2f}%) "
                        f"abaixo do máximo ({alert['taxa_max']:.2f}%)"
                    )
                
                if triggered:
                    alert_copy = alert.copy()
                    alert_copy['message'] = " | ".join(message)
                    alerts_triggered.append(alert_copy)
        
        return alerts_triggered
    
    def send_alert_email(self, alert):
        """
        Envia email de alerta para o usuário usando o Brevo.
        
        Args:
            alert (pd.Series): Dados do alerta acionado
        """
        if not EMAIL_USER or not EMAIL_PASSWORD:
            raise ValueError("Credenciais de email não configuradas")
        
        # Criar mensagem
        msg = MIMEMultipart()
        msg['From'] = 'psgrigoletti@gmail.com'
        msg['To'] = alert['email']
        msg['Subject'] = f"Alerta Tesouro Direto - {alert['tipo_titulo']}"
        
        # Corpo do email
        body = f"""
        Olá {alert['nome']},
        
        Seu alerta para o título {alert['tipo_titulo']} ({alert['ano_vencimento']}) foi acionado!
        
        Motivo: {alert['message']}
        
        Atenciosamente,
        Sistema de Alertas Tesouro Direto
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        try:
            # Configurar conexão com o servidor SMTP do Brevo
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.ehlo()  # Identificação com o servidor
            server.starttls()  # Iniciar TLS
            server.ehlo()  # Reidentificação após TLS
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            
            # Enviar email
            server.send_message(msg)
            server.quit()
        except Exception as e:
            raise Exception(f"Erro ao enviar email: {str(e)}") 