#!/usr/bin/env python3
"""
Agendador Inteligente de Upload
Sistema que define horários ótimos para upload baseado em estratégias de engagement
"""

import json
import random
from datetime import datetime, timedelta, time
from typing import List, Dict, Tuple
import logging

logger = logging.getLogger(__name__)

class SmartScheduler:
    """Agendador inteligente para uploads do YouTube"""
    
    def __init__(self):
        self.optimal_times = self._load_optimal_times()
        self.timezone_offset = -3  # UTC-3 (Brasília)
        
    def _load_optimal_times(self) -> Dict:
        """Carrega horários ótimos baseados em dados de engagement"""
        return {
            "segunda": {
                "prime_times": [
                    {"hour": 7, "minute": 0, "score": 85},   # Manhã - pessoas indo trabalhar
                    {"hour": 12, "minute": 30, "score": 90}, # Almoço
                    {"hour": 18, "minute": 0, "score": 95},  # Saída do trabalho
                    {"hour": 21, "minute": 0, "score": 88}   # Noite
                ],
                "good_times": [
                    {"hour": 9, "minute": 0, "score": 75},
                    {"hour": 15, "minute": 30, "score": 70},
                    {"hour": 22, "minute": 30, "score": 65}
                ]
            },
            "terca": {
                "prime_times": [
                    {"hour": 8, "minute": 0, "score": 88},
                    {"hour": 12, "minute": 0, "score": 92},
                    {"hour": 17, "minute": 30, "score": 96},
                    {"hour": 20, "minute": 30, "score": 90}
                ],
                "good_times": [
                    {"hour": 10, "minute": 30, "score": 78},
                    {"hour": 14, "minute": 30, "score": 73},
                    {"hour": 22, "minute": 0, "score": 68}
                ]
            },
            "quarta": {
                "prime_times": [
                    {"hour": 7, "minute": 30, "score": 87},
                    {"hour": 12, "minute": 15, "score": 94},
                    {"hour": 18, "minute": 15, "score": 97},  # Melhor horário da semana
                    {"hour": 21, "minute": 15, "score": 89}
                ],
                "good_times": [
                    {"hour": 9, "minute": 30, "score": 76},
                    {"hour": 15, "minute": 0, "score": 74},
                    {"hour": 23, "minute": 0, "score": 63}
                ]
            },
            "quinta": {
                "prime_times": [
                    {"hour": 8, "minute": 30, "score": 86},
                    {"hour": 12, "minute": 45, "score": 91},
                    {"hour": 17, "minute": 45, "score": 95},
                    {"hour": 20, "minute": 45, "score": 92}
                ],
                "good_times": [
                    {"hour": 10, "minute": 0, "score": 77},
                    {"hour": 14, "minute": 15, "score": 72},
                    {"hour": 22, "minute": 15, "score": 69}
                ]
            },
            "sexta": {
                "prime_times": [
                    {"hour": 7, "minute": 15, "score": 83},   # Sexta de manhã é menor
                    {"hour": 11, "minute": 45, "score": 89},
                    {"hour": 17, "minute": 0, "score": 93},   # Pessoas saindo para weekend
                    {"hour": 19, "minute": 30, "score": 85}   # Início da noite
                ],
                "good_times": [
                    {"hour": 9, "minute": 15, "score": 74},
                    {"hour": 14, "minute": 0, "score": 71},
                    {"hour": 21, "minute": 30, "score": 67}   # Pessoas em baladas
                ]
            },
            "sabado": {
                "prime_times": [
                    {"hour": 10, "minute": 0, "score": 81},   # Manhã mais tarde
                    {"hour": 14, "minute": 30, "score": 84},  # Tarde
                    {"hour": 16, "minute": 30, "score": 86},  # Final da tarde
                    {"hour": 20, "minute": 0, "score": 82}    # Noite
                ],
                "good_times": [
                    {"hour": 12, "minute": 0, "score": 78},
                    {"hour": 18, "minute": 30, "score": 75},
                    {"hour": 22, "minute": 0, "score": 70}
                ]
            },
            "domingo": {
                "prime_times": [
                    {"hour": 11, "minute": 0, "score": 79},   # Manhã bem tarde
                    {"hour": 15, "minute": 0, "score": 88},   # Tarde - pico do domingo
                    {"hour": 17, "minute": 30, "score": 85},  # Final da tarde
                    {"hour": 19, "minute": 45, "score": 87}   # Noite - preparação segunda
                ],
                "good_times": [
                    {"hour": 13, "minute": 30, "score": 80},
                    {"hour": 21, "minute": 0, "score": 76},
                    {"hour": 22, "minute": 30, "score": 72}
                ]
            }
        }
    
    def get_optimal_schedule(self, num_videos: int, start_date: datetime = None,
                           strategy: str = "balanced") -> List[Dict]:
        """
        Gera cronograma otimizado para múltiplos vídeos
        
        Args:
            num_videos: Número de vídeos para agendar
            start_date: Data de início (padrão: hoje)
            strategy: "aggressive" (mais posts/dia), "balanced" ou "conservative"
            
        Returns:
            Lista com horários agendados
        """
        logger.info(f"Gerando cronograma para {num_videos} vídeos - estratégia: {strategy}")
        
        if start_date is None:
            start_date = datetime.now()
        
        # Configurar estratégia
        strategy_config = {
            "aggressive": {"posts_per_day": 4, "min_interval_hours": 2},
            "balanced": {"posts_per_day": 2, "min_interval_hours": 4},
            "conservative": {"posts_per_day": 1, "min_interval_hours": 8}
        }
        
        config = strategy_config.get(strategy, strategy_config["balanced"])
        posts_per_day = config["posts_per_day"]
        min_interval = config["min_interval_hours"]
        
        schedule = []
        current_date = start_date
        videos_scheduled = 0
        
        while videos_scheduled < num_videos:
            # Obter horários do dia
            day_name = self._get_day_name(current_date)
            day_times = self._get_day_optimal_times(day_name, posts_per_day)
            
            for time_slot in day_times:
                if videos_scheduled >= num_videos:
                    break
                
                # Criar datetime completo
                scheduled_time = datetime.combine(
                    current_date.date(),
                    time(time_slot["hour"], time_slot["minute"])
                )
                
                # Verificar se não é muito cedo (não agendar para menos de 1 hora)
                if scheduled_time <= datetime.now() + timedelta(hours=1):
                    continue
                
                schedule.append({
                    "video_number": videos_scheduled + 1,
                    "scheduled_time": scheduled_time,
                    "day_name": day_name,
                    "engagement_score": time_slot["score"],
                    "time_category": time_slot.get("category", "prime")
                })
                
                videos_scheduled += 1
            
            current_date += timedelta(days=1)
            
            # Proteção contra loop infinito
            if current_date > start_date + timedelta(days=30):
                logger.warning("Limite de 30 dias atingido para agendamento")
                break
        
        # Ordenar por horário
        schedule.sort(key=lambda x: x["scheduled_time"])
        
        logger.info(f"Cronograma gerado: {len(schedule)} vídeos em {len(set(s['scheduled_time'].date() for s in schedule))} dias")
        
        return schedule
    
    def _get_day_name(self, date: datetime) -> str:
        """Converte datetime para nome do dia em português"""
        day_names = {
            0: "segunda", 1: "terca", 2: "quarta", 3: "quinta",
            4: "sexta", 5: "sabado", 6: "domingo"
        }
        return day_names[date.weekday()]
    
    def _get_day_optimal_times(self, day_name: str, num_posts: int) -> List[Dict]:
        """Retorna os melhores horários para um dia específico"""
        
        day_data = self.optimal_times.get(day_name, self.optimal_times["quarta"])
        
        # Combinar prime_times e good_times
        all_times = []
        
        # Adicionar categoria aos horários
        for time_slot in day_data["prime_times"]:
            time_slot["category"] = "prime"
            all_times.append(time_slot)
        
        for time_slot in day_data["good_times"]:
            time_slot["category"] = "good"
            all_times.append(time_slot)
        
        # Ordenar por score (maior primeiro)
        all_times.sort(key=lambda x: x["score"], reverse=True)
        
        # Selecionar os melhores horários
        selected_times = []
        for i in range(min(num_posts, len(all_times))):
            selected_times.append(all_times[i])
        
        # Se precisar de mais horários, adicionar variações
        while len(selected_times) < num_posts and len(all_times) > 0:
            base_time = random.choice(all_times[:3])  # Pegar dos 3 melhores
            # Adicionar variação de ±30 minutos
            variation = random.choice([-30, -15, 15, 30])
            new_hour = base_time["hour"]
            new_minute = base_time["minute"] + variation
            
            # Ajustar minutos e horas
            if new_minute >= 60:
                new_hour += 1
                new_minute -= 60
            elif new_minute < 0:
                new_hour -= 1
                new_minute += 60
            
            # Verificar se horário é válido (6h às 23h59m)
            if 6 <= new_hour <= 23:
                selected_times.append({
                    "hour": new_hour,
                    "minute": new_minute,
                    "score": base_time["score"] - 5,  # Slightly lower score for variations
                    "category": "variation"
                })
        
        return selected_times[:num_posts]
    
    def get_next_optimal_time(self, from_datetime: datetime = None) -> datetime:
        """Retorna o próximo horário ótimo para upload"""
        
        if from_datetime is None:
            from_datetime = datetime.now()
        
        # Procurar nos próximos 7 dias
        for days_ahead in range(7):
            check_date = from_datetime + timedelta(days=days_ahead)
            day_name = self._get_day_name(check_date)
            
            # Pegar melhor horário do dia
            day_times = self._get_day_optimal_times(day_name, 1)
            if day_times:
                best_time = day_times[0]
                scheduled_time = datetime.combine(
                    check_date.date(),
                    time(best_time["hour"], best_time["minute"])
                )
                
                # Se é hoje, verificar se horário ainda não passou
                if check_date.date() == from_datetime.date():
                    if scheduled_time <= from_datetime:
                        continue
                
                return scheduled_time
        
        # Fallback: amanhã às 12h
        return from_datetime + timedelta(days=1, hours=12)
    
    def calculate_engagement_score(self, scheduled_time: datetime) -> int:
        """Calcula score de engagement esperado para um horário"""
        
        day_name = self._get_day_name(scheduled_time)
        hour = scheduled_time.hour
        minute = scheduled_time.minute
        
        day_data = self.optimal_times.get(day_name, self.optimal_times["quarta"])
        
        # Procurar horário exato ou mais próximo
        best_score = 50  # Score padrão
        
        for time_slot in day_data["prime_times"] + day_data["good_times"]:
            # Calcular diferença em minutos
            slot_minutes = time_slot["hour"] * 60 + time_slot["minute"]
            target_minutes = hour * 60 + minute
            diff_minutes = abs(slot_minutes - target_minutes)
            
            # Se muito próximo (±15min), usar score completo
            if diff_minutes <= 15:
                best_score = max(best_score, time_slot["score"])
            # Se próximo (±30min), usar score reduzido
            elif diff_minutes <= 30:
                best_score = max(best_score, time_slot["score"] - 10)
            # Se razoavelmente próximo (±60min), usar score bem reduzido
            elif diff_minutes <= 60:
                best_score = max(best_score, time_slot["score"] - 20)
        
        return best_score
    
    def optimize_existing_schedule(self, schedule: List[Dict]) -> List[Dict]:
        """Otimiza um cronograma existente"""
        
        logger.info(f"Otimizando cronograma de {len(schedule)} vídeos")
        
        optimized = []
        for item in schedule:
            if "scheduled_time" in item:
                # Recalcular score
                score = self.calculate_engagement_score(item["scheduled_time"])
                item["engagement_score"] = score
                
                # Sugerir melhor horário se score muito baixo
                if score < 60:
                    better_time = self.get_next_optimal_time(item["scheduled_time"])
                    item["suggested_time"] = better_time
                    item["suggested_score"] = self.calculate_engagement_score(better_time)
            
            optimized.append(item)
        
        return optimized
    
    def generate_schedule_report(self, schedule: List[Dict]) -> str:
        """Gera relatório detalhado do cronograma"""
        
        if not schedule:
            return "Nenhum vídeo agendado."
        
        report = "📅 CRONOGRAMA OTIMIZADO DE UPLOADS\n"
        report += "=" * 50 + "\n\n"
        
        # Estatísticas gerais
        total_videos = len(schedule)
        days_span = (schedule[-1]["scheduled_time"] - schedule[0]["scheduled_time"]).days + 1
        avg_score = sum(s["engagement_score"] for s in schedule) / total_videos
        
        report += f"📊 RESUMO:\n"
        report += f"   • Total de vídeos: {total_videos}\n"
        report += f"   • Período: {days_span} dias\n"
        report += f"   • Score médio de engagement: {avg_score:.1f}\n"
        report += f"   • Vídeos/dia: {total_videos/days_span:.1f}\n\n"
        
        # Cronograma detalhado
        report += f"🗓️ CRONOGRAMA DETALHADO:\n"
        
        current_date = None
        for item in schedule:
            scheduled_time = item["scheduled_time"]
            
            # Cabeçalho do dia se mudou
            if current_date != scheduled_time.date():
                current_date = scheduled_time.date()
                day_name = self._get_day_name(scheduled_time).title()
                report += f"\n📅 {day_name}, {scheduled_time.strftime('%d/%m/%Y')}:\n"
            
            # Detalhes do vídeo
            score_emoji = "🔥" if item["engagement_score"] >= 90 else "⚡" if item["engagement_score"] >= 75 else "📈"
            report += f"   {score_emoji} {scheduled_time.strftime('%H:%M')} - Vídeo {item['video_number']} "
            report += f"(Score: {item['engagement_score']})\n"
        
        # Recomendações
        report += f"\n💡 RECOMENDAÇÕES:\n"
        high_score_count = sum(1 for s in schedule if s["engagement_score"] >= 85)
        if high_score_count / total_videos >= 0.7:
            report += "   ✅ Excelente distribuição de horários!\n"
        else:
            report += "   ⚠️ Considere redistribuir alguns vídeos para horários de maior engagement.\n"
        
        return report