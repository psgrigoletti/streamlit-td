import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from datetime import datetime


class AlertManager:
    def __init__(self, alerts_file='alerts.csv'):
        self.alerts_file = alerts_file
        self._load_alerts()
    
    def _load_alerts(self):
        """Carrega os alertas do arquivo CSV."""
        if os.path.exists(self.alerts_file):
            self.alerts = pd.read_csv(self.alerts_file)
        else:
            self.alerts = pd.DataFrame(columns=[
                'nome', 'email', 'tipo_titulo', 'ano_vencimento',
                'preco_min', 'preco_max', 'taxa_min', 'taxa_max',
                'data_criacao'
            ])
    
    def _save_alerts(self):
        """Salva os alertas no arquivo CSV."""
        self.alerts.to_csv(self.alerts_file, index=False)
    
    def add_alert(self, nome, email, tipo_titulo, ano_vencimento,
                  preco_min=None, preco_max=None, taxa_min=None, taxa_max=None):
        """Adiciona um novo alerta."""
        new_alert = {
            'nome': nome,
            'email': email,
            'tipo_titulo': tipo_titulo,
            'ano_vencimento': ano_vencimento,
            'preco_min': preco_min,
            'preco_max': preco_max,
            'taxa_min': taxa_min,
            'taxa_max': taxa_max,
            'data_criacao': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        self.alerts = pd.concat(
            [self.alerts, pd.DataFrame([new_alert])],
            ignore_index=True
        )
        self._save_alerts()
    
    def remove_alert(self, index):
        """Remove um alerta pelo índice."""
        if 0 <= index < len(self.alerts):
            self.alerts = self.alerts.drop(index).reset_index(drop=True)
            self._save_alerts()
            return True
        return False
    
    def check_alerts(self, df):
        """Verifica se algum título atende aos critérios dos alertas."""
        alerts_triggered = []
        
        for _, alert in self.alerts.iterrows():
            # Filtrar dados para o título e ano específicos
            df_filtered = df[
                (df['Tipo Titulo'] == alert['tipo_titulo']) &
                (df['Ano Vencimento'] == alert['ano_vencimento'])
            ]
            
            if not df_filtered.empty:
                latest_data = df_filtered.iloc[-1]  # Dados mais recentes
                
                # Verificar condições de preço
                price_condition = True
                if pd.notna(alert['preco_min']):
                    price_condition &= latest_data['PU Compra Manha'] >= alert['preco_min']
                if pd.notna(alert['preco_max']):
                    price_condition &= latest_data['PU Compra Manha'] <= alert['preco_max']
                
                # Verificar condições de taxa
                rate_condition = True
                if pd.notna(alert['taxa_min']):
                    rate_condition &= latest_data['Taxa Compra Manha'] >= alert['taxa_min']
                if pd.notna(alert['taxa_max']):
                    rate_condition &= latest_data['Taxa Compra Manha'] <= alert['taxa_max']
                
                if price_condition and rate_condition:
                    alerts_triggered.append({
                        'nome': alert['nome'],
                        'email': alert['email'],
                        'tipo_titulo': alert['tipo_titulo'],
                        'ano_vencimento': alert['ano_vencimento'],
                        'preco_atual': latest_data['PU Compra Manha'],
                        'taxa_atual': latest_data['Taxa Compra Manha']
                    })
        
        return alerts_triggered
    
    def send_alert_email(self, alert):
        """Envia email de alerta."""
        # Configurações do servidor SMTP (exemplo usando Gmail)
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        sender_email = os.getenv("ALERT_EMAIL")
        sender_password = os.getenv("ALERT_EMAIL_PASSWORD")
        
        if not all([sender_email, sender_password]):
            raise ValueError("Email credentials not configured")
        
        # Criar mensagem
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = alert['email']
        message["Subject"] = "Alerta de Tesouro Direto"
        
        # Corpo do email
        body = f"""
        Olá {alert['nome']},
        
        Um título do Tesouro Direto atende aos seus critérios de alerta:
        
        Título: {alert['tipo_titulo']}
        Ano de Vencimento: {alert['ano_vencimento']}
        Preço Atual: R$ {alert['preco_atual']:.2f}
        Taxa Atual: {alert['taxa_atual']:.2f}%
        
        Acesse o sistema para mais detalhes.
        """
        
        message.attach(MIMEText(body, "plain"))
        
        # Enviar email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(message) 